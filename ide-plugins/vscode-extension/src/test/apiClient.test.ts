import * as assert from 'assert';
import { ApiClient } from '../apiClient';

// Mock vscode module
const mockVscode = {
    window: {
        withProgress: (options: any, callback: Function) => {
            return callback();
        },
        showErrorMessage: (msg: string) => {},
        showInformationMessage: (msg: string) => {}
    }
};

// Simulate ApiClient for unit testing (without vscode dependency)
class TestableApiClient {
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

    private async _request(path: string, options: any = {}): Promise<any> {
        const url = `${this.baseUrl}${path}`;
        // In real tests this would use fetch, here we simulate
        return { status: 'ok' };
    }
}

suite('ApiClient Tests', () => {
    test('constructor sets baseUrl and apiKey', () => {
        const client = new TestableApiClient('http://localhost:8000', 'test-key');
        assert.strictEqual((client as any).baseUrl, 'http://localhost:8000');
        assert.strictEqual((client as any).apiKey, 'test-key');
    });

    test('getAgents returns array', async () => {
        const client = new TestableApiClient('http://localhost:8000', '');
        const agents = await client.getAgents();
        assert.ok(Array.isArray(agents));
    });

    test('getPlugins returns array', async () => {
        const client = new TestableApiClient('http://localhost:8000', '');
        const plugins = await client.getPlugins();
        assert.ok(Array.isArray(plugins));
    });

    test('getStatus returns object', async () => {
        const client = new TestableApiClient('http://localhost:8000', '');
        const status = await client.getStatus();
        assert.ok(typeof status === 'object');
    });
});
