import * as vscode from 'vscode';

export class ApiClient {
	constructor(private baseUrl: string, private apiKey: string) {}

	async getStatus(): Promise<any> {
		return this._request('/api/status');
	}

	async getAgents(): Promise<any[]> {
		return this._request('/api/agents') || [];
	}

	async getPlugins(): Promise<any[]> {
		return this._request('/api/plugins') || [];
	}

	async callAgent(agentId: string, input: string): Promise<string> {
		const result = await this._request(`/api/agents/${agentId}/call`, {
			method: 'POST',
			body: JSON.stringify({ input })
		});
		return result?.response || '';
	}

	async installPlugin(pluginId: string): Promise<boolean> {
		try {
			await this._request('/api/plugins/install', {
				method: 'POST',
				body: JSON.stringify({ plugin_id: pluginId })
			});
			return true;
		} catch {
			return false;
		}
	}

	private async _request(path: string, options: any = {}): Promise<any> {
		const url = `${this.baseUrl}${path}`;
		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
			...(this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {})
		};

		const response = await vscode.window.withProgress(
			{
				location: vscode.ProgressLocation.Notification,
				title: `AstrBot API: ${path}`,
				cancellable: false
			},
			() => fetch(url, {
				...options,
				headers
			})
		);

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		return response.json();
	}
}
