import * as vscode from 'vscode';
import { ApiClient } from './apiClient';

export class AstrBotStatusPanel {
	public static currentPanel: AstrBotStatusPanel | undefined;
	private readonly _panel: vscode.WebviewPanel;
	private readonly _extensionUri: vscode.Uri;
	private readonly _apiClient: ApiClient;
	private _disposables: vscode.Disposable[] = [];

	constructor(extensionUri: vscode.Uri, apiClient: ApiClient) {
		this._extensionUri = extensionUri;
		this._apiClient = apiClient;

		this._panel = vscode.window.createWebviewPanel(
			'astrbotStatus',
			'AstrBot Status',
			vscode.ViewColumn.Two,
			{ retainContextWhenHidden: true }
		);

	 AstrBotStatusPanel.currentPanel = this;
		this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

		this._panel.webview.html = this._getHtmlForWebview();
		this.refresh();
	}

	public refresh() {
		this._updateStatus();
	}

	private async _updateStatus() {
		try {
			const status = await this._apiClient.getStatus();
			const agents = await this._apiClient.getAgents();
			const plugins = await this._apiClient.getPlugins();

			this._panel.webview.html = this._getHtmlForWebview(status, agents, plugins);
		} catch (error) {
			this._panel.webview.html = this._getHtmlForWebview(
				null, [], [],
				`Error: ${error instanceof Error ? error.message : 'Unknown error'}`
			);
		}
	}

	private _getHtmlForWebview(
		status: any = null,
		agents: any[] = [],
		plugins: any[] = [],
		error: string = ''
	): string {
		const version = status?.bot_version || 'Unknown';
		const uptime = status?.uptime ? this._formatUptime(status.uptime) : '--';
		const agentList = agents.length > 0
			? agents.map((a: any) => `<li><span class="status-${a.status}">●</span> ${a.name} (${a.type})</li>`).join('')
			: '<li>No agents available</li>';
		const pluginList = plugins.length > 0
			? plugins.map((p: any) => `<li>${p.name} v${p.version}</li>`).join('')
			: '<li>No plugins installed</li>';

		return `<!DOCTYPE html>
<html>
<head>
	<style>
		body { font-family: var(--vscode-font-family); padding: 10px; background: var(--vscode-editor-background); color: var(--vscode-foreground); }
		h2 { color: var(--vscode-textLink-foreground); margin-top: 0; }
		.section { margin-bottom: 20px; }
		.section h3 { margin-bottom: 8px; color: var(--vscode-foreground); }
		.status-active { color: #4caf50; }
		.status-inactive { color: #ff9800; }
		.grid { display: grid; grid-template-columns: 100px 1fr; gap: 5px; }
		.grid-label { font-weight: bold; }
		button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 6px 12px; cursor: pointer; }
		button:hover { background: var(--vscode-button-hoverBackground); }
		.error { color: #f44336; }
		ul { margin: 5px 0; padding-left: 20px; }
	</style>
</head>
<body>
	<h2>AstrBot Status</h2>
	<div class="section">
		<h3>Info</h3>
		<div class="grid">
			<span class="grid-label">Version:</span><span>${version}</span>
			<span class="grid-label">Uptime:</span><span>${uptime}</span>
		</div>
		<button onclick="refresh()">Refresh</button>
	</div>
	${error ? `<p class="error">${error}</p>` : ''}
	<div class="section">
		<h3>Agents (${agents.length})</h3>
		<ul>${agentList}</ul>
	</div>
	<div class="section">
		<h3>Plugins (${plugins.length})</h3>
		<ul>${pluginList}</ul>
	</div>
	<script>
		const vscode = acquireVsCodeApi();
		function refresh() { vscode.postMessage({ command: 'refresh' }); }
		window.addEventListener('message', e => {
			if (e.data.command === 'update') { location.reload(); }
		});
	</script>
</body>
</html>`;
	}

	private _formatUptime(seconds: number): string {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
	}

	dispose() {
	 AstrBotStatusPanel.currentPanel = undefined;
		this._panel.dispose();
		while (this._disposables.length) {
			this._disposables.pop()?.dispose();
		}
	}
}
