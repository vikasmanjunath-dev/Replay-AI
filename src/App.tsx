import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { Activity, ArrowRight, Check, CircleAlert, FileArchive, LoaderCircle, Monitor, Moon, Save, ShieldCheck, Sun, Trash2, UploadCloud, X } from 'lucide-react';
import { AbortableRequests } from './abortableRequests.js';
import { describeRequestError } from './userFacingError.js';
import { getSessionBadgeLabel } from './dashboardLabels.js';
import { readStorage, removeStorage, writeStorage } from './safeStorage.js';

type TimelineEvent = { timestamp: string; stage: string; status: string; actor?: string; correlation_id?: string | null; details: Record<string, unknown> };
type Task = {
  task_id: string; status: string; current_stage: string; bug_report: string; created_at: string;
  triage?: { title: string; severity: string; acceptance_criteria: string[]; rationale?: string };
  investigation_patch?: { buggy_file: string; root_cause: string; confidence_score: number; files_changed: string[]; unified_diff: string; summary_of_changes: string };
  sandbox_result?: { test_command: string; tests_passed: boolean; exit_code: number; stdout: string; stderr: string; isolation_mode: string; applied_patch_cleanly: boolean };
  reviewer?: { security_assessment: string; recommendation: string; review_summary: string; regression_risks: string[]; side_effects: string[] };
  error?: { failed_stage: string; message: string }; evidence_timeline: TimelineEvent[]; is_approved?: boolean;
  is_applied?: boolean; is_committed?: boolean; commit_hash?: string | null;
  commit_message?: string | null;
  repository_id?: string | null; repository_base_revision?: string | null; repository_result_revision?: string | null;
  repository_operation_state?: string | null;
};
type Scenario = { id: string; name: string; description: string; bug_report: string; codebase: Record<string, string> };
type Session = { actor: string; role: 'viewer' | 'operator' };
type RepositoryTarget = { repository_id: string; branch: string; revision: string; clean: boolean };
type ActionAudit = { action_id: number; actor: string; action: string; outcome: string; notes?: string | null; details: Record<string, unknown>; created_at: string };
type PullRequestResult = { repository: string; number: number; url: string; state: string; already_open: boolean };
type GitHubRepository = { id: number; full_name: string; private: boolean; default_branch: string; html_url: string };
type Readiness = { status: 'checking' | 'ready' | 'degraded' | 'offline' | 'auth'; detail?: string };
type ThemePreference = 'system' | 'light' | 'dark';
type ApiErrorPayload = { detail?: unknown; request_id?: unknown };
class ApiError extends Error {
  constructor(message: string, readonly status: number, readonly payload: ApiErrorPayload) {
    super(message);
    this.name = 'ApiError';
  }
}
const READINESS_LABELS: Record<Readiness['status'], string> = {
  checking: 'CHECKING',
  ready: 'READY',
  degraded: 'DEGRADED',
  offline: 'OFFLINE',
  auth: 'AUTH REQUIRED',
};
const THEME_LABELS: Record<ThemePreference, string> = { system: 'System', light: 'Light', dark: 'Dark' };
const NEXT_THEME: Record<ThemePreference, ThemePreference> = { system: 'light', light: 'dark', dark: 'system' };
const API = (import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')).replace(/\/$/, '');

async function api<T>(path: string, init?: RequestInit, onResponse?: (response: Response) => void): Promise<T> {
  const headers = new Headers(init?.headers);
  const token = readStorage('session', 'relay-api-token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({})) as ApiErrorPayload;
    const detail = typeof body.detail === 'string' ? body.detail : `API request failed (${response.status})`;
    const requestId = response.headers.get('X-Request-ID') || (typeof body.request_id === 'string' ? body.request_id : '');
    throw new ApiError(requestId ? `${detail} (Request ID: ${requestId})` : detail, response.status, body);
  }
  onResponse?.(response);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function safeGitHubUrl(value: unknown): string | null {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' && url.origin === 'https://github.com' ? url.href : null;
  } catch { return null; }
}

function isGitHubRepository(value: unknown): value is GitHubRepository {
  if (!value || typeof value !== 'object') return false;
  const repository = value as Partial<GitHubRepository>;
  return Number.isSafeInteger(repository.id) && typeof repository.full_name === 'string'
    && typeof repository.private === 'boolean' && typeof repository.default_branch === 'string'
    && repository.default_branch.trim().length > 0 && safeGitHubUrl(repository.html_url) !== null;
}

export default function App() {
  const [themePreference, setThemePreference] = useState<ThemePreference>(() => {
    const saved = readStorage('local', 'relay-theme');
    return saved === 'light' || saved === 'dark' ? saved : 'system';
  });
  const [systemDark, setSystemDark] = useState(() => window.matchMedia('(prefers-color-scheme: dark)').matches);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [task, setTask] = useState<Task | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [repositoryTargets, setRepositoryTargets] = useState<RepositoryTarget[]>([]);
  const [repositoryId, setRepositoryId] = useState('');
  const [report, setReport] = useState('');
  const [snapshot, setSnapshot] = useState('');
  const [archive, setArchive] = useState<File | null>(null);
  const [inputMode, setInputMode] = useState<'map' | 'zip'>('map');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [apiToken, setApiToken] = useState(() => readStorage('session', 'relay-api-token') || '');
  const [tokenRevision, setTokenRevision] = useState(0);
  const [readiness, setReadiness] = useState<Readiness>({ status: 'checking' });
  const [readinessChecking, setReadinessChecking] = useState(false);
  const readinessCheckInFlight = useRef(false);
  const [refreshRequests] = useState(() => new AbortableRequests());
  const [taskSearch, setTaskSearch] = useState('');
  const [taskStatus, setTaskStatus] = useState('');
  const [taskPageOffset, setTaskPageOffset] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);
  const [session, setSession] = useState<Session>({ actor: '', role: 'viewer' });
  const [actions, setActions] = useState<ActionAudit[]>([]);
  const [totalActions, setTotalActions] = useState(0);
  const [actionPageOffset, setActionPageOffset] = useState(0);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [totalEvents, setTotalEvents] = useState(0);
  const [eventPageOffset, setEventPageOffset] = useState(0);
  const [reviewNotes, setReviewNotes] = useState('');
  const [commitMessage, setCommitMessage] = useState('');
  const [prHead, setPrHead] = useState('');
  const [prBase, setPrBase] = useState('');
  const [prTitle, setPrTitle] = useState('');
  const [prBody, setPrBody] = useState('');
  const [prDraft, setPrDraft] = useState(false);
  const [pullRequest, setPullRequest] = useState<PullRequestResult | null>(null);
  const [pullRequestTaskId, setPullRequestTaskId] = useState('');
  const [githubRepository, setGithubRepository] = useState<GitHubRepository | null>(null);
  const [githubRepositoryError, setGithubRepositoryError] = useState('');

  const resolvedTheme = themePreference === 'system' ? (systemDark ? 'dark' : 'light') : themePreference;
  useEffect(() => {
    const preference = window.matchMedia('(prefers-color-scheme: dark)');
    const update = (event: MediaQueryListEvent) => setSystemDark(event.matches);
    setSystemDark(preference.matches);
    preference.addEventListener('change', update);
    return () => preference.removeEventListener('change', update);
  }, []);
  useLayoutEffect(() => {
    document.documentElement.dataset.theme = resolvedTheme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', resolvedTheme === 'dark' ? '#0b0b0d' : '#f5f5f7');
    if (themePreference === 'system') removeStorage('local', 'relay-theme');
    else writeStorage('local', 'relay-theme', themePreference);
  }, [resolvedTheme, themePreference]);

  function cycleTheme() {
    setThemePreference((current) => current === 'system' ? 'light' : current === 'light' ? 'dark' : 'system');
  }

  const refresh = useCallback(async () => {
    const requests = refreshRequests;
    const controller = requests.start();
    try {
      const params = new URLSearchParams({ limit: '50', offset: String(taskPageOffset) });
      if (taskSearch.trim()) params.set('q', taskSearch.trim());
      if (taskStatus) params.set('status', taskStatus);
      const selectedId = task?.task_id;
      let nextTotalTasks = 0;
      let nextTotalActions = 0;
      let nextTotalEvents = 0;
      const [list, demos, selectedDetail, selectedActions, selectedEvents, currentSession] = await Promise.all([
        api<Task[]>(`/api/v1/tasks?${params}`, { signal: controller.signal }, (response) => { nextTotalTasks = Number(response.headers.get('X-Total-Count') || 0); }),
        api<Scenario[]>('/api/v1/scenarios', { signal: controller.signal }),
        selectedId ? api<Task>(`/api/v1/tasks/${selectedId}`, { signal: controller.signal }).catch(() => null) : Promise.resolve(null),
        selectedId ? api<ActionAudit[]>(`/api/v1/tasks/${selectedId}/actions?limit=50&offset=${actionPageOffset}`, { signal: controller.signal }, (response) => { nextTotalActions = Number(response.headers.get('X-Total-Count') || 0); }).catch(() => []) : Promise.resolve([]),
        selectedId ? api<TimelineEvent[]>(`/api/v1/tasks/${selectedId}/events?limit=50&offset=${eventPageOffset}`, { signal: controller.signal }, (response) => { nextTotalEvents = Number(response.headers.get('X-Total-Count') || 0); }).catch(() => []) : Promise.resolve([]),
        api<Session>('/api/v1/session', { signal: controller.signal }),
      ]);
      if (!requests.isCurrent(controller)) return;
      setTasks(list); setScenarios(demos);
      setSession(currentSession);
      setTotalTasks(nextTotalTasks); setTotalActions(nextTotalActions); setTotalEvents(nextTotalEvents);
      setActions(selectedActions);
      setEvents(selectedEvents);
      setTask((current) => current ? (list.find((item) => item.task_id === current.task_id) || selectedDetail || current) : current);
      setError('');
    } catch (reason) {
      if (requests.isCurrent(controller)) {
        setError(describeRequestError(reason, 'Could not load tasks.'));
      }
    } finally {
      requests.finish(controller);
    }
  }, [taskSearch, taskStatus, taskPageOffset, task?.task_id, eventPageOffset, actionPageOffset]);
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => () => refreshRequests.cancel(), [refreshRequests]);
  const checkReadiness = useCallback(async () => {
    if (readinessCheckInFlight.current) return;
    readinessCheckInFlight.current = true;
    setReadinessChecking(true);
    try {
      await api<{ status: string }>('/ready', { signal: AbortSignal.timeout(8_000) });
      setReadiness({ status: 'ready' });
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : '';
      if (reason instanceof ApiError && reason.status === 503) {
        const payloadDetail = reason.payload.detail;
        const missing = payloadDetail && typeof payloadDetail === 'object'
          ? (payloadDetail as { missing?: unknown }).missing
          : undefined;
        const issues = Array.isArray(missing) ? missing.filter((item): item is string => typeof item === 'string') : [];
        setReadiness({ status: 'degraded', detail: issues.join(' · ') || 'A required pipeline dependency is unavailable.' });
      } else if (reason instanceof ApiError && reason.status === 401) {
        setReadiness({ status: 'auth', detail: 'Save a valid API token to check service readiness.' });
      } else if (reason instanceof DOMException && reason.name === 'TimeoutError') {
        setReadiness({ status: 'offline', detail: 'The readiness check timed out. The API may be unavailable or overloaded.' });
      } else if (reason instanceof TypeError || /failed to fetch|network|fetch/i.test(detail)) {
        setReadiness({ status: 'offline', detail: 'The dashboard cannot reach the API.' });
      } else {
        setReadiness({ status: 'degraded', detail: 'The readiness check did not complete successfully.' });
      }
    } finally {
      readinessCheckInFlight.current = false;
      setReadinessChecking(false);
    }
  }, []);
  useEffect(() => {
    void checkReadiness();
    const timer = window.setInterval(() => { void checkReadiness(); }, 30_000);
    return () => window.clearInterval(timer);
  }, [checkReadiness, tokenRevision]);
  useEffect(() => {
    if (!session.actor) return;
    let active = true;
    void api<RepositoryTarget[]>('/api/v1/repositories').then((targets) => { if (active) setRepositoryTargets(targets); }).catch(() => { if (active) setRepositoryTargets([]); });
    return () => { active = false; };
  }, [session.actor]);
  useEffect(() => {
    if (!task || ['AWAITING_HUMAN_APPROVAL', 'APPROVED', 'APPLIED', 'COMMITTED', 'REJECTED', 'FAILED', 'CANCELLED'].includes(task.status)) return;
    const timer = window.setInterval(() => { void refresh(); }, 1800);
    return () => window.clearInterval(timer);
  }, [task?.task_id, task?.status, refresh]);
  useEffect(() => {
    if (session.role !== 'operator' || !task?.is_committed || !task.repository_id) {
      setGithubRepository(null); setGithubRepositoryError('');
      return;
    }
    let active = true;
    setGithubRepository(null); setGithubRepositoryError('');
    void api<unknown>(`/api/v1/github/repositories/${encodeURIComponent(task.repository_id)}`)
      .then((repository) => {
        if (!active) return;
        if (!isGitHubRepository(repository)) throw new Error('GitHub returned incomplete repository metadata.');
        setGithubRepository(repository);
        setPrBase(repository.default_branch);
      })
      .catch((reason) => { if (active) setGithubRepositoryError(describeRequestError(reason, 'GitHub repository is not available.')); });
    return () => { active = false; };
  }, [session.role, task?.task_id, task?.is_committed, task?.repository_id]);
  useEffect(() => {
    if (!task?.task_id || !task.is_committed) return;
    setPrHead('');
    setPrBase('');
    setPrTitle((task.triage?.title || '').slice(0, 200));
    const summary = task.investigation_patch?.summary_of_changes || task.investigation_patch?.root_cause || task.bug_report;
    const verification = task.sandbox_result?.tests_passed ? 'Tests passed in the recorded sandbox run.' : 'See the task evidence for sandbox results.';
    setPrBody(`## Summary\n${summary}\n\n## Verification\n${verification}`.slice(0, 20_000));
    setPrDraft(false);
    setPullRequest(null);
    setPullRequestTaskId('');
  }, [task?.task_id, task?.is_committed, task?.triage?.title, task?.investigation_patch?.summary_of_changes, task?.investigation_patch?.root_cause, task?.bug_report, task?.sandbox_result?.tests_passed]);

  async function submit() {
    setBusy(true); setError(''); setMessage('');
    try {
      let created: Task;
      if (inputMode === 'zip' && archive) {
        const body = new FormData(); body.append('bug_report', report); body.append('file', archive);
        if (repositoryId) body.append('repository_id', repositoryId);
        created = await api<Task>('/api/v1/tasks/upload', { method: 'POST', body });
      } else {
        const codebase = JSON.parse(snapshot) as Record<string, string>;
        created = await api<Task>('/api/v1/tasks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chat_message: report, codebase, repository_id: repositoryId || null }) });
      }
      setTask(created); setActions([]); setTotalActions(0); setActionPageOffset(0); setEvents([]); setTotalEvents(0); setEventPageOffset(0); setReviewNotes(''); setCommitMessage(''); setMessage('Task queued. Progress and evidence will appear here.'); await refresh();
    } catch (reason) { setError(describeRequestError(reason, 'Submission failed.')); }
    finally { setBusy(false); }
  }

  async function act(action: 'approve' | 'reject' | 'apply' | 'commit' | 'cancel' | 'retry') {
    if (!task) return;
    setBusy(true); setError('');
    const keySlot = `relay-action-key:${task.task_id}:${action}`;
    const idempotencyKey = readStorage('session', keySlot) || crypto.randomUUID();
    writeStorage('session', keySlot, idempotencyKey);
    try {
      const effectiveCommitMessage = task.repository_operation_state === 'COMMITTING' ? task.commit_message?.trim() || '' : commitMessage.trim();
      const payload = { action, ...(['approve', 'reject'].includes(action) && reviewNotes.trim() ? { notes: reviewNotes.trim() } : {}), ...(action === 'commit' && effectiveCommitMessage ? { commit_message: effectiveCommitMessage } : {}) };
      const updated = await api<Task>(`/api/v1/tasks/${task.task_id}/actions`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey }, body: JSON.stringify(payload) });
      removeStorage('session', keySlot);
      setTask(updated);
      setMessage(({ approve: 'Patch approved.', reject: 'Patch rejected.', apply: updated.repository_id ? `Patch applied to ${updated.repository_id}.` : 'Patch applied to its task workspace.', commit: `Created Git commit ${updated.commit_hash || ''}.`, cancel: 'Cancellation requested.', retry: 'Task queued for retry.' })[action]);
      await refresh();
    } catch (reason) { setError(describeRequestError(reason, 'Action failed.')); }
    finally { setBusy(false); }
  }

  async function openPullRequest() {
    if (!task) return;
    setBusy(true); setError(''); setMessage('');
    const keySlot = `relay-action-key:${task.task_id}:open_pull_request`;
    const idempotencyKey = readStorage('session', keySlot) || crypto.randomUUID();
    writeStorage('session', keySlot, idempotencyKey);
    try {
      const result = await api<PullRequestResult>(`/api/v1/tasks/${task.task_id}/pull-request`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey },
        body: JSON.stringify({ head_branch: prHead.trim(), base_branch: prBase.trim(), title: prTitle.trim(), body: prBody.trim(), draft: prDraft }),
      });
      removeStorage('session', keySlot);
      setPullRequest(result);
      setPullRequestTaskId(task.task_id);
      setMessage(result.already_open ? `Pull request #${result.number} is already open.` : `Opened pull request #${result.number}.`);
      await refresh();
    } catch (reason) { setError(describeRequestError(reason, 'Could not open pull request.')); }
    finally { setBusy(false); }
  }

  async function copyRevision(label: string, revision: string) {
    try {
      await navigator.clipboard.writeText(revision);
      setError(''); setMessage(`${label} copied to clipboard.`);
    } catch {
      setError('Clipboard access is unavailable. Select the displayed revision and copy it manually.');
    }
  }

  async function deleteTask(item: Task) {
    const title = item.triage?.title || item.bug_report.slice(0, 90);
    if (!window.confirm(`Permanently delete “${title}”, its evidence, uploaded source snapshot, and task workspace?`)) return;
    setBusy(true); setError(''); setMessage('');
    try {
      await api<void>(`/api/v1/tasks/${item.task_id}`, { method: 'DELETE' });
      if (task?.task_id === item.task_id) setTask(null);
      setMessage('Task and its stored source data were deleted.');
      await refresh();
    } catch (reason) { setError(describeRequestError(reason, 'Task deletion failed.')); }
    finally { setBusy(false); }
  }

  function loadScenario(item: Scenario) { setReport(item.bug_report); setSnapshot(JSON.stringify(item.codebase, null, 2)); setArchive(null); setInputMode('map'); setRepositoryId(''); setMessage(`${item.name} loaded.`); }
  function saveToken() {
    if (apiToken.trim()) {
      const persistent = writeStorage('session', 'relay-api-token', apiToken.trim());
      setMessage(persistent
        ? 'API token saved for this tab session.'
        : 'Browser storage is blocked; the token will remain available only until this page reloads or closes.');
    } else {
      removeStorage('session', 'relay-api-token');
      setMessage('API token removed from this tab session.');
    }
    setTokenRevision((revision) => revision + 1);
    void refresh();
  }
  async function downloadPatch() {
    if (!task?.investigation_patch) return;
    try {
      const headers = new Headers();
      const token = readStorage('session', 'relay-api-token');
      if (token) headers.set('Authorization', `Bearer ${token}`);
      const response = await fetch(`${API}/api/v1/tasks/${task.task_id}/patch`, { headers });
      if (!response.ok) throw new Error(`Patch download failed (${response.status})`);
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement('a'); link.href = url; link.download = `relay-${task.task_id}.patch`; link.click();
      URL.revokeObjectURL(url);
    } catch (reason) { setError(describeRequestError(reason, 'Patch download failed.')); }
  }

  const recordedPullRequest = actions.find((entry) => entry.action === 'open_pull_request' && safeGitHubUrl(entry.details.url));
  const recordedPullRequestUrl = safeGitHubUrl(recordedPullRequest?.details.url);
  const recordedPullRequestNumber = typeof recordedPullRequest?.details.number === 'number' ? recordedPullRequest.details.number : '—';
  const recordedPullRequestState = typeof recordedPullRequest?.outcome === 'string' ? recordedPullRequest.outcome : 'open';
  const visiblePullRequest = pullRequestTaskId === task?.task_id && pullRequest ? pullRequest : null;
  return <div className="layout">
    <a className="skip-link sr-only" href="#main-content">Skip to main content</a>
    <aside className="sidebar">
      <div className="brand"><span className="brand-icon">R</span><div><b>relay<span>.ai</span></b><small>ENGINEERING PIPELINE</small></div></div>
      <div className="side-caption">WORKSPACE</div><div className="nav-current"><Activity size={16}/> Pipeline</div>
      <div className="side-caption recent-caption">TASKS <span>{totalTasks}</span></div>
      <div className="task-filters"><input aria-label="Search tasks" value={taskSearch} onChange={(e) => { setTaskSearch(e.target.value); setTaskPageOffset(0); }} placeholder="Search tasks"/><select aria-label="Filter tasks by status" value={taskStatus} onChange={(e) => { setTaskStatus(e.target.value); setTaskPageOffset(0); }}><option value="">All statuses</option>{['RECEIVED','QUEUED','RUNNING','TRIAGING','TRIAGED','INVESTIGATING','INVESTIGATED','PATCHED','SANDBOX_RUNNING','SANDBOX_TESTED','REVIEWING','REVIEWED','AWAITING_HUMAN_APPROVAL','APPROVED','APPLIED','COMMITTED','REJECTED','CANCELLED','FAILED'].map((s) => <option key={s} value={s}>{s.replaceAll('_',' ')}</option>)}</select></div>
      <div className="task-list">{tasks.map((item) => <div key={item.task_id} className="task-row"><button className={`task-link ${task?.task_id === item.task_id ? 'selected' : ''}`} onClick={() => { setTask(item); setActions([]); setTotalActions(0); setActionPageOffset(0); setEvents([]); setTotalEvents(0); setEventPageOffset(0); setReviewNotes(''); setCommitMessage(''); }}><i className={`dot ${item.status.toLowerCase()}`}/><span><b>{item.triage?.title || item.bug_report}</b><small>{item.status.replaceAll('_', ' ')}</small></span></button>{session.role === 'operator' && <button className="task-delete" aria-label={`Delete task ${item.triage?.title || item.task_id}`} title="Delete task and stored source" disabled={busy} onClick={() => void deleteTask(item)}><Trash2 size={13}/></button>}</div>)}{!tasks.length && <p className="side-empty">Submitted tasks will appear here.</p>}</div>
      <div className="task-pagination"><button disabled={taskPageOffset === 0} onClick={() => setTaskPageOffset(Math.max(0, taskPageOffset - 50))}>Newer</button><span>{totalTasks ? `${taskPageOffset + 1}–${Math.min(taskPageOffset + tasks.length, totalTasks)}` : '0 tasks'}</span><button disabled={taskPageOffset + 50 >= totalTasks} onClick={() => setTaskPageOffset(taskPageOffset + 50)}>Older</button></div>
      <div className="side-bottom"><i/> API <span>{API ? API.replace(/^https?:\/\//, '') : window.location.host}</span></div>
    </aside>
    <main id="main-content" className="main" tabIndex={-1}>
      <header className="topbar"><span>RELAY AI <b>/</b> Autonomous pipeline</span><div className="top-actions"><small className={`readiness-badge ${readiness.status}`} aria-live="polite" aria-label={`Pipeline service: ${READINESS_LABELS[readiness.status]}${readiness.detail ? `. ${readiness.detail}` : ''}`} title={readiness.detail || 'Pipeline service readiness'}>{READINESS_LABELS[readiness.status]}</small><small className="session-badge">{getSessionBadgeLabel(session, readiness.status)}</small><input aria-label="Optional API token" type="password" value={apiToken} onChange={(e) => setApiToken(e.target.value)} placeholder="API token (optional)"/><button onClick={saveToken} aria-label="Save API token"><Save size={13}/><span>Save</span></button><button onClick={() => void refresh()} aria-label="Refresh tasks"><Activity size={14}/><span>Refresh</span></button><button className="theme-control" onClick={cycleTheme} aria-label={`Appearance: ${THEME_LABELS[themePreference]}. Activate to use ${THEME_LABELS[NEXT_THEME[themePreference]]}.`} title={`Appearance: ${THEME_LABELS[themePreference]} · Next: ${THEME_LABELS[NEXT_THEME[themePreference]]}`}><span className="theme-control-icon">{themePreference === 'system' ? <Monitor size={14}/> : resolvedTheme === 'dark' ? <Moon size={14}/> : <Sun size={14}/>}</span><span>{THEME_LABELS[themePreference]}</span></button></div></header>
      <div className="content">
        <div className="heading"><div><small>ENGINEERING AUTOMATION</small><h1>Issue remediation</h1><p>Turn a bug report into a reviewed patch with test evidence and a human decision.</p></div><span className="pipeline-label"><i/> 3-stage pipeline</span></div>
        {readiness.status !== 'ready' && readiness.status !== 'checking' && <div className={`readiness-notice ${readiness.status}`} role={readiness.status === 'offline' ? 'alert' : 'status'}><span><b>Pipeline service: {READINESS_LABELS[readiness.status]}</b><small>{readiness.detail}</small></span><button disabled={readinessChecking} onClick={() => void checkReadiness()} aria-label="Check pipeline service readiness again">{readinessChecking ? 'Checking…' : 'Check again'}</button></div>}
        <label className="mobile-task-picker">Recent task<select aria-label="Select a recent task" value={task?.task_id || ''} onChange={(event) => { setTask(tasks.find((item) => item.task_id === event.target.value) || null); setActions([]); setTotalActions(0); setActionPageOffset(0); setEvents([]); setTotalEvents(0); setEventPageOffset(0); setReviewNotes(''); setCommitMessage(''); }}><option value="">Select a task</option>{tasks.map((item) => <option key={item.task_id} value={item.task_id}>{item.triage?.title || item.bug_report.slice(0, 70)} · {item.status.replaceAll('_', ' ')}</option>)}</select></label>
        <div className="mobile-task-filters"><input aria-label="Search tasks" value={taskSearch} onChange={(e) => { setTaskSearch(e.target.value); setTaskPageOffset(0); }} placeholder="Search tasks"/><select aria-label="Filter tasks by status" value={taskStatus} onChange={(e) => { setTaskStatus(e.target.value); setTaskPageOffset(0); }}><option value="">All statuses</option>{['RECEIVED','QUEUED','RUNNING','TRIAGING','TRIAGED','INVESTIGATING','INVESTIGATED','PATCHED','SANDBOX_RUNNING','SANDBOX_TESTED','REVIEWING','REVIEWED','AWAITING_HUMAN_APPROVAL','APPROVED','APPLIED','COMMITTED','REJECTED','CANCELLED','FAILED'].map((s) => <option key={s} value={s}>{s.replaceAll('_',' ')}</option>)}</select></div>
        <div className="mobile-task-pagination"><button disabled={taskPageOffset === 0} onClick={() => setTaskPageOffset(Math.max(0, taskPageOffset - 50))}>Newer tasks</button><span>{totalTasks ? `${taskPageOffset + 1}–${Math.min(taskPageOffset + tasks.length, totalTasks)} of ${totalTasks}` : 'No tasks'}</span><button disabled={taskPageOffset + 50 >= totalTasks} onClick={() => setTaskPageOffset(taskPageOffset + 50)}>Older tasks</button></div>
        {(error || message) && <div className={`notice ${error ? 'notice-error' : ''}`} role={error ? 'alert' : 'status'}><span>{error || message}</span><button aria-label="Dismiss notification" onClick={() => { setError(''); setMessage(''); }}><X size={15}/></button></div>}
        <div className={`columns ${session.role === 'viewer' ? 'viewer-columns' : ''}`}>
          {session.role === 'operator' && <section className="panel submit-panel"><div className="panel-heading"><i>01</i><div><h2>New remediation task</h2><p>Describe the defect and provide its codebase.</p></div></div>
            <label className="field-label" htmlFor="report">BUG REPORT</label><textarea id="report" className="report" maxLength={20000} value={report} onChange={(e) => setReport(e.target.value)} placeholder="What is broken? Include expected and actual behavior, errors, and relevant context."/>
            <label className="field-label" htmlFor="repository-target">APPLY TARGET · OPTIONAL</label><select id="repository-target" className="action-input" value={repositoryId} onChange={(e) => setRepositoryId(e.target.value)}><option value="">Task-owned copy (default)</option>{repositoryTargets.map((target) => <option key={target.repository_id} value={target.repository_id} disabled={!target.clean}>{target.repository_id} · {target.branch || 'detached'} · {target.revision.slice(0, 10)}{target.clean ? '' : ' · has local changes'}</option>)}</select>{!repositoryTargets.length && <small className="target-help">No local Git targets are configured. The default uses an isolated task-owned copy.</small>}
            <div className="divider">CODEBASE INPUT</div>
            <div className="input-options" role="group" aria-labelledby="codebase-input-label"><span id="codebase-input-label" className="sr-only">Codebase input type</span><label className={inputMode === 'map' ? 'option active-option' : 'option'}><input type="radio" name="codebase-input" checked={inputMode === 'map'} onChange={() => { setInputMode('map'); setArchive(null); }}/><UploadCloud size={18}/><span><b>Paste file map</b><small>JSON paths and contents</small></span></label><label className={inputMode === 'zip' ? 'option active-option' : 'option'}><input type="radio" name="codebase-input" checked={inputMode === 'zip'} onChange={() => setInputMode('zip')}/><FileArchive size={18}/><span><b>Upload ZIP</b><small>{archive?.name || 'Python repository'}</small></span></label></div>
            {inputMode === 'map' ? <textarea aria-label="Repository file map as JSON" className="snapshot" value={snapshot} onChange={(e) => setSnapshot(e.target.value)} spellCheck={false} placeholder={'{\n  "calculator.py": "def add(a, b): return a + b\\n",\n  "test_calculator.py": "..."\n}'}/> : <div className="archive-picker"><label htmlFor="archive">ZIP archive</label><input key={inputMode} id="archive" type="file" accept=".zip" onChange={(e) => setArchive(e.target.files?.[0] || null)}/><small>Choose a repository archive up to 25 MiB.</small></div>}
            <div className="submit-footer"><span>1.5 MB source context · up to 500 files</span><button className="primary" disabled={busy || report.trim().length < 5 || (inputMode === 'map' ? !snapshot.trim() : !archive)} onClick={() => void submit()}>{busy ? <><LoaderCircle className="spin" size={16}/> Working</> : <>Run pipeline <ArrowRight size={16}/></>}</button></div>
            <div className="demos"><small>LOAD A DEMO SCENARIO</small>{scenarios.map((item) => <button key={item.id} onClick={() => loadScenario(item)}>{item.name.replace(/^Scenario \d+: /, '')}<ArrowRight size={13}/></button>)}</div>
          </section>}
          <section className="panel results-panel">{!task ? <div className="no-task"><span><Activity size={25}/></span><h2>Your pipeline results</h2><p>Submit a report to see triage, patch details, test evidence, and reviewer findings here.</p><div>01 Triage　·　02 Investigate　·　03 Review</div></div> : <>
            <div className="panel-heading"><i>02</i><div><h2>Task review</h2><p className="task-id">{task.task_id}</p>{task.repository_id && <p className="task-id">Target {task.repository_id} · base {task.repository_base_revision?.slice(0, 12)}</p>}</div><span className="badge">{task.status.replaceAll('_', ' ')}</span></div>
            {task.error && <div className="error-card"><CircleAlert size={18}/><span><b>{task.error.failed_stage}</b><br/>{task.error.message}</span></div>}
            {task.triage && <div className="result-section"><div className="result-title"><h3>{task.triage.title}</h3><span className="severity">{task.triage.severity}</span></div><p>{task.triage.rationale}</p><b>Acceptance criteria</b>{task.triage.acceptance_criteria.map((item, i) => <div className="criterion" key={i}><Check size={14}/>{item}</div>)}</div>}
            {task.investigation_patch && <div className="result-section"><small className="kicker">ROOT CAUSE · {Math.round(task.investigation_patch.confidence_score * 100)}% CONFIDENCE</small><p>{task.investigation_patch.root_cause}</p><b>Changed files</b><div className="file-tags">{task.investigation_patch.files_changed.map((file) => <code key={file}>{file}</code>)}</div><details><summary>View unified diff</summary><pre>{task.investigation_patch.unified_diff}</pre></details><button className="patch-download" onClick={() => void downloadPatch()}>Download patch file</button></div>}
            {task.sandbox_result && <div className="evidence"><div><b><Activity size={15}/> Sandbox execution</b><span className={task.sandbox_result.tests_passed ? 'pass' : 'fail'}>{task.sandbox_result.tests_passed ? 'TESTS PASSED' : 'TESTS FAILED'}</span></div><small>Exit {task.sandbox_result.exit_code} · {task.sandbox_result.isolation_mode} · Patch {task.sandbox_result.applied_patch_cleanly ? 'applied' : 'rejected'}</small><code className="test-command">{task.sandbox_result.test_command}</code><details><summary>Execution output</summary>{task.sandbox_result.stdout && <section><b>stdout</b><pre>{task.sandbox_result.stdout}</pre></section>}{task.sandbox_result.stderr && <section><b>stderr</b><pre>{task.sandbox_result.stderr}</pre></section>}{!task.sandbox_result.stdout && !task.sandbox_result.stderr && <p>No output captured.</p>}</details></div>}
            {task.reviewer && <div className="review"><b><ShieldCheck size={16}/> AI reviewer <span>{task.reviewer.security_assessment} · {task.reviewer.recommendation}</span></b><p>{task.reviewer.review_summary}</p>{task.reviewer.regression_risks.map((risk, i) => <div className="criterion risk" key={i}><CircleAlert size={14}/>{risk}</div>)}</div>}
            {session.role === 'operator' && task.status === 'AWAITING_HUMAN_APPROVAL' && <><label className="field-label" htmlFor="review-notes">REVIEW NOTES · OPTIONAL</label><textarea id="review-notes" className="action-input" maxLength={2000} value={reviewNotes} onChange={(e) => { setReviewNotes(e.target.value); removeStorage('session', `relay-action-key:${task.task_id}:approve`); removeStorage('session', `relay-action-key:${task.task_id}:reject`); }} placeholder="Record the reason for your decision."/><div className="decisions"><button disabled={busy} onClick={() => void act('reject')}><X size={15}/> Reject</button><button disabled={busy} onClick={() => void act('approve')}><Check size={15}/> Approve patch</button></div></>}
            {session.role === 'operator' && !['AWAITING_HUMAN_APPROVAL', 'APPROVED', 'APPLIED', 'COMMITTED', 'REJECTED', 'CANCELLED', 'FAILED'].includes(task.status) && <div className="decisions"><button disabled={busy} onClick={() => void act('cancel')}><X size={15}/> Cancel task</button></div>}
            {session.role === 'operator' && task.status === 'FAILED' && <div className="decisions"><button disabled={busy} onClick={() => void act('retry')}>Retry task</button></div>}
            {session.role === 'operator' && task.is_approved && !task.is_applied && <div className="decisions"><button disabled={busy} onClick={() => void act('apply')}><Check size={15}/> Apply to {task.repository_id || 'task workspace'}</button></div>}
            {session.role === 'operator' && task.is_applied && !task.is_committed && <><label className="field-label" htmlFor="commit-message">COMMIT MESSAGE · OPTIONAL</label><input id="commit-message" className="action-input" maxLength={200} readOnly={task.repository_operation_state === 'COMMITTING'} value={task.repository_operation_state === 'COMMITTING' ? task.commit_message || '' : commitMessage} onChange={(e) => { setCommitMessage(e.target.value); removeStorage('session', `relay-action-key:${task.task_id}:commit`); }} placeholder="Uses a generated message when blank."/>{task.repository_operation_state === 'COMMITTING' && <small className="target-help">Resuming the pending commit with its recorded message.</small>}<div className="decisions"><span className="pending">Patch applied to {task.repository_id || 'isolated task copy'}.</span><button disabled={busy} onClick={() => void act('commit')}><Check size={15}/>{task.repository_operation_state === 'COMMITTING' ? 'Resume commit' : 'Commit'}</button></div></>}
            {task.is_committed && task.commit_hash && <div className="commit-record"><b>Commit {task.commit_hash.slice(0, 12)}</b><code>{task.commit_message}</code><code className="revision-value">{task.commit_hash}</code><button className="copy-revision" onClick={() => void copyRevision('Commit SHA', task.commit_hash!)}>Copy commit SHA</button></div>}
            {task.is_committed && <div className="pending">Committed to {task.repository_id || 'task copy'} · {task.commit_hash}</div>}
            {session.role === 'operator' && task.is_committed && task.repository_id && <section className="github-pr" aria-label="Open GitHub pull request">
              <div className="divider">OPEN GITHUB PULL REQUEST</div>
              {githubRepository && <p className="target-help" role="status" aria-live="polite">Connected repository: <a href={githubRepository.html_url} target="_blank" rel="noreferrer">{githubRepository.full_name}</a></p>}
              {githubRepositoryError && <p className="target-help" role="alert">{githubRepositoryError} Check that this repository is in the backend GitHub allow-list.</p>}
              <p className="target-help">Publish the task commit to the head branch first. Its base must match this task’s recorded base revision; Relay checks both exact SHAs before opening the PR.</p>
              {task.repository_base_revision && <div className="revision-row"><span><small>EXPECTED BASE</small><code>{task.repository_base_revision}</code></span><button className="copy-revision" onClick={() => void copyRevision('Base SHA', task.repository_base_revision!)}>Copy base SHA</button></div>}
              <label className="field-label" htmlFor="pr-head">PUBLISHED HEAD BRANCH</label><input id="pr-head" className="action-input" maxLength={240} value={prHead} onChange={(event) => { setPrHead(event.target.value); removeStorage('session', `relay-action-key:${task.task_id}:open_pull_request`); }} placeholder="feature/fix-checkout"/>
              <label className="field-label" htmlFor="pr-base">BASE BRANCH</label><input id="pr-base" className="action-input" maxLength={240} value={prBase} onChange={(event) => { setPrBase(event.target.value); removeStorage('session', `relay-action-key:${task.task_id}:open_pull_request`); }} placeholder="main"/>
              <label className="field-label" htmlFor="pr-title">TITLE</label><input id="pr-title" className="action-input" maxLength={200} value={prTitle} onChange={(event) => { setPrTitle(event.target.value); removeStorage('session', `relay-action-key:${task.task_id}:open_pull_request`); }} placeholder={task.triage?.title || 'Fix'} />
              <label className="field-label" htmlFor="pr-body">DESCRIPTION · OPTIONAL</label><textarea id="pr-body" className="action-input" maxLength={20000} value={prBody} onChange={(event) => { setPrBody(event.target.value); removeStorage('session', `relay-action-key:${task.task_id}:open_pull_request`); }} placeholder="Summarize the fix and verification." />
              <label className="pr-draft"><input type="checkbox" checked={prDraft} onChange={(event) => { setPrDraft(event.target.checked); removeStorage('session', `relay-action-key:${task.task_id}:open_pull_request`); }}/> Create as draft</label>
              <div className="decisions"><button className="primary" disabled={busy || !prHead.trim() || !prBase.trim() || !prTitle.trim()} onClick={() => void openPullRequest()}>Open pull request <ArrowRight size={15}/></button></div>
            </section>}
            {(visiblePullRequest || recordedPullRequestUrl) && <div className="commit-record"><b>Pull request #{visiblePullRequest?.number ?? recordedPullRequestNumber} · {visiblePullRequest?.state || recordedPullRequestState}</b><a href={visiblePullRequest ? safeGitHubUrl(visiblePullRequest.url) || undefined : recordedPullRequestUrl || undefined} target="_blank" rel="noreferrer">View on GitHub</a></div>}
            <div className="timeline"><small className="kicker">ACTIVITY · {totalEvents ? `${Math.max(1, totalEvents - eventPageOffset - events.length + 1)}–${totalEvents - eventPageOffset} OF ${totalEvents} EVENTS` : '0 EVENTS'}</small>{events.map((event, i) => <div key={`${event.timestamp}-${event.stage}-${i}`}><i/><span><b>{event.stage.replaceAll('_', ' ')}</b><small>{event.status} · {event.actor || 'system'} · {new Date(event.timestamp).toLocaleString()}</small>{event.stage === 'MODEL_USAGE' && <div className="model-usage"><small>{String(event.details.provider || 'provider')} · {String(event.details.model || 'unknown model')}</small><small>{String(event.details.prompt_tokens ?? 0)} prompt · {String(event.details.candidate_tokens ?? 0)} generated · {String(event.details.total_tokens ?? 0)} total tokens</small>{event.details.estimated_cost_usd != null && <small>Estimated ${String(event.details.estimated_cost_usd)} · {String(event.details.pricing_label || 'operator pricing')}</small>}</div>}</span></div>)}{!events.length && <p className="side-empty">No activity events on this page.</p>}<div className="event-pagination"><button disabled={eventPageOffset === 0} onClick={() => setEventPageOffset(Math.max(0, eventPageOffset - 50))}>Newer events</button><button disabled={eventPageOffset + events.length >= totalEvents} onClick={() => setEventPageOffset(eventPageOffset + 50)}>Older events</button></div></div>
            <div className="timeline action-audit"><small className="kicker">OPERATOR ACTION AUDIT · {totalActions ? `${Math.max(1, totalActions - actionPageOffset - actions.length + 1)}–${totalActions - actionPageOffset} OF ${totalActions} RECORDS` : '0 RECORDS'}</small>{actions.map((entry) => <div key={entry.action_id}><i/><span><b>{entry.action.replaceAll('_', ' ')} · {entry.outcome}</b><small>{entry.actor} · {new Date(entry.created_at).toLocaleString()}</small>{entry.notes && <p>{entry.notes}</p>}<details><summary>Action details</summary><pre>{JSON.stringify(entry.details, null, 2)}</pre></details></span></div>)}{!actions.length && <p className="side-empty">No operator actions recorded.</p>}<div className="event-pagination"><button disabled={actionPageOffset === 0} onClick={() => setActionPageOffset(Math.max(0, actionPageOffset - 50))}>Newer actions</button><button disabled={actionPageOffset + actions.length >= totalActions} onClick={() => setActionPageOffset(actionPageOffset + 50)}>Older actions</button></div></div>
          </>}</section>
        </div>
        <footer>RELAY AI · Human review remains required for every patch.<span>Local workspace</span></footer>
      </div>
    </main>
  </div>;
}
