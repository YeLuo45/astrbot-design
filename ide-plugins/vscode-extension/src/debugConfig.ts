import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

export class DebugConfigProvider {
	private readonly ATTACH_PORT = 5678;
	private readonly ATTACH_HOST = 'localhost';

	async generateAttachConfig() {
		const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
		if (!workspaceFolder) {
			vscode.window.showErrorMessage('No workspace folder open');
			return;
		}

		const vscodeDir = path.join(workspaceFolder.uri.fsPath, '.vscode');
		const launchPath = path.join(vscodeDir, 'launch.json');

		let launchConfig: any = { version: '0.2.0', configurations: [] };

		if (fs.existsSync(launchPath)) {
			try {
				const existing = fs.readFileSync(launchPath, 'utf-8');
				launchConfig = JSON.parse(existing);
				if (!launchConfig.configurations) {
					launchConfig.configurations = [];
				}
			} catch {}
		}

		// Add AstrBot attach configuration
		const astrbotConfig = {
			name: 'AstrBot: Attach to Bot',
			type: 'python',
			request: 'attach',
			connect: {
				host: this.ATTACH_HOST,
				port: this.ATTACH_PORT
			},
			preLaunchTask: 'astrbot:start',
		 justMyCode: false,
			logToFile: true
		};

		// Add AstrBot run configuration
		const astrbotRunConfig = {
			name: 'AstrBot: Run Plugin Test',
			type: 'python',
			request: 'launch',
			module: 'pytest',
			args: ['tests/', '-v', '--tb=short'],
			cwd: '${workspaceFolder}',
			env: {
				ASTRBOT_API_URL: 'http://localhost:8000',
				ASTRBOT_API_KEY: ''
			},
			console: 'integratedTerminal'
		};

		launchConfig.configurations.push(astrbotConfig, astrbotRunConfig);

		// Ensure .vscode directory exists
		if (!fs.existsSync(vscodeDir)) {
			fs.mkdirSync(vscodeDir, { recursive: true });
		}

		fs.writeFileSync(launchPath, JSON.stringify(launchConfig, null, 4));

		vscode.window.showInformationMessage(
			'AstrBot debug configurations added to .vscode/launch.json',
			'Open launch.json'
		).then(choice => {
			if (choice === 'Open launch.json') {
				vscode.window.showTextDocument(vscode.Uri.file(launchPath));
			}
		});
	}
}
