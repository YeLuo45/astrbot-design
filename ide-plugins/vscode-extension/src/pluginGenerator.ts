import * as vscode from 'vscode';
import * as path from 'path';

export class PluginGenerator {
	private readonly TEMPLATE_PATH = path.join(__dirname, '..', 'templates', 'basic-plugin');

	async createNewPlugin() {
		const name = await vscode.window.showInputBox({
			prompt: 'Enter plugin name (e.g., my-plugin)',
			validateInput: (value) => {
				if (!value || value.trim() === '') return 'Name cannot be empty';
				if (!/^[a-z0-9-]+$/.test(value)) return 'Use lowercase letters, numbers, and hyphens only';
				return null;
			}
		});

		if (!name) return;

		const description = await vscode.window.showInputBox({
			prompt: 'Enter plugin description',
			value: `AstrBot plugin: ${name}`
		}) || name;

		const author = await vscode.window.showInputBox({
			prompt: 'Enter author name',
			value: vscode.env.username || 'AstrBot Developer'
		}) || 'AstrBot Developer';

		await this._generatePlugin(name, description, author);
	}

	private async _generatePlugin(name: string, description: string, author: string) {
		const workspacePath = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
		if (!workspacePath) {
			vscode.window.showErrorMessage('Please open a workspace first');
			return;
		}

		const pluginPath = vscode.Uri.file(path.join(workspacePath, name));

		try {
			await vscode.workspace.fs.createDirectory(pluginPath);

			// Generate plugin.json
			const pluginJson = {
				id: name.toLowerCase().replace(/-/g, '_'),
				name,
				version: '0.1.0',
				description,
				author,
				dependencies: {}
			};
			await vscode.workspace.fs.writeFile(
				vscode.Uri.joinPath(pluginPath, 'plugin.json'),
				new TextEncoder().encode(JSON.stringify(pluginJson, null, 2))
			);

			// Generate __init__.py
			const initPy = `# ${name} - AstrBot Plugin
from .plugin import Plugin

__all__ = ["Plugin"]
`;
			await vscode.workspace.fs.writeFile(
				vscode.Uri.joinPath(pluginPath, '__init__.py'),
				new TextEncoder().encode(initPy)
			);

			// Generate plugin.py
			const pluginPy = `# ${name} - Main plugin class
from astrbot import Plugin as BasePlugin
from astrbot.event import filter, AstrBotMessage

class Plugin(BasePlugin):
    """AstrBot plugin: ${name}"""

    async def activate(self):
        """Called when plugin is activated."""
        self.logger.info(f"${name} plugin activated")

    async def deactivate(self):
        """Called when plugin is deactivated."""
        self.logger.info(f"${name} plugin deactivated")

    @filter.event()
    async def on_message(self, event: AstrBotMessage):
        """Handle incoming messages."""
        pass
`;
			await vscode.workspace.fs.writeFile(
				vscode.Uri.joinPath(pluginPath, 'plugin.py'),
				new TextEncoder().encode(pluginPy)
			);

			// Generate pyproject.toml
			const pyproject = `[project]
name = "${name}"
version = "0.1.0"
description = "${description}"
requires-python = ">=3.10"

[project.astrbot-plugin]
handler = "${name}.plugin:Plugin"
`;
			await vscode.workspace.fs.writeFile(
				vscode.Uri.joinPath(pluginPath, 'pyproject.toml'),
				new TextEncoder().encode(pyproject)
			);

			// Generate README.md
			const readme = `# ${name}

${description}

## Installation

\`\`\`bash
astrbot plugin install -e ./${name}
\`\`\`

## Usage

TODO: Add usage instructions.

## Author

${author}
`;
			await vscode.workspace.fs.writeFile(
				vscode.Uri.joinPath(pluginPath, 'README.md'),
				new TextEncoder().encode(readme)
			);

			vscode.window.showInformationMessage(
				`Plugin "${name}" created successfully at ${path.join(workspacePath, name)}`,
				'Open in Explorer'
			).then(choice => {
				if (choice === 'Open in Explorer') {
					vscode.env.openExternal(vscode.Uri.file(path.join(workspacePath, name)));
				}
			});

		} catch (error) {
			vscode.window.showErrorMessage(
				`Failed to create plugin: ${error instanceof Error ? error.message : 'Unknown error'}`
			);
		}
	}
}
