import * as vscode from 'vscode';
import { AstrBotStatusPanel } from './statusPanel';
import { PluginGenerator } from './pluginGenerator';
import { ApiClient } from './apiClient';
import { DebugConfigProvider } from './debugConfig';

let statusPanel: AstrBotStatusPanel | undefined;
let apiClient: ApiClient;

export function activate(context: vscode.ExtensionContext) {
	const config = vscode.workspace.getConfiguration('astrbot');
	apiClient = new ApiClient(
		config.get<string>('apiUrl', 'http://localhost:8000'),
		config.get<string>('apiKey', '')
	);

	// Register status panel
	statusPanel = new AstrBotStatusPanel(context.extensionUri, apiClient);

	// Register commands
	const commands = [
		vscode.commands.registerCommand('astrbot-helper.refreshStatus', () => {
			statusPanel?.refresh();
		}),
		vscode.commands.registerCommand('astrbot-helper.newPlugin', async () => {
			const generator = new PluginGenerator();
			await generator.createNewPlugin();
		}),
		vscode.commands.registerCommand('astrbot-helper.openRepl', async () => {
			const terminal = vscode.window.createTerminal('AstrBot REPL');
			terminal.sendText('astrbot repl');
			terminal.show();
		}),
		vscode.commands.registerCommand('astrbot-helper.attachDebugger', async () => {
			const provider = new DebugConfigProvider();
			await provider.generateAttachConfig();
		})
	];

	// Register tree view
	vscode.window.registerTreeDataProvider('astrbotHelperView', {
		getTreeItem: (element: AstrBotTreeItem) => element,
		getChildren: () => {
			return [
				new AstrBotTreeItem('Status', '$(circle-outline)', 'Click refresh to load'),
				new AstrBotTreeItem('Agents', '$(person)', 'Click refresh to load'),
				new AstrBotTreeItem('Plugins', '$(package)', 'Click refresh to load')
			];
		}
	});

	// Register configuration provider for debug
	vscode.debug.registerDebugConfigurationProvider('python', {
		provideDebugConfigurations: (folder) => {
			return [
				{
					name: 'AstrBot: Attach',
					type: 'python',
					request: 'attach',
					connect: { host: 'localhost', port: 5678 },
					preLaunchTask: 'astrbot:start'
				}
			];
		}
	});

	context.subscriptions.push(...commands);
}

export function deactivate() {}

class AstrBotTreeItem extends vscode.TreeItem {
	constructor(
		public readonly label: string,
		public readonly iconPath: string,
		public readonly description: string
	) {
		super(label, vscode.TreeItemCollapsibleState.None);
		this.iconPath = new vscode.ThemeIcon(iconPath);
		this.tooltip = description;
	}
}
