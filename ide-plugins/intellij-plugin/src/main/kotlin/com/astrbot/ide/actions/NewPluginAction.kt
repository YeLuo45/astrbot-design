package com.astrbot.ide.actions

import com.intellij.openapi.actionSystem.*
import com.intellij.openapi.application.*
import com.intellij.openapi.ui.*
import com.intellij.openapi.project.*
import java.awt.*
import javax.swing.*

/**
 * Action to generate a new AstrBot plugin from template.
 * Triggered via menu: File -> New -> AstrBot Plugin
 */
class NewPluginAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        showDialog(project)
    }

    private fun showDialog(project: Project) {
        val dialog = NewPluginDialog(project)
        dialog.show()
    }
}

class NewPluginDialog(project: Project) : DialogWrapper(project) {
    private lateinit var nameField: JTextField
    private lateinit var descriptionField: JTextField
    private lateinit var authorField: JTextField
    private var selectedTemplate = "basic"

    init {
        title = "New AstrBot Plugin"
        init()
    }

    override fun createCenterPanel(): JComponent {
        val panel = JPanel(GridBagLayout())
        panel.preferredSize = Dimension(400, 200)

        val constraints = GridBagConstraints()
        constraints.insets = Insets(5, 5, 5, 5)
        constraints.fill = GridBagConstraints.HORIZONTAL
        constraints.weightx = 1.0

        // Plugin name
        constraints.gridy = 0
        constraints.gridx = 0
        panel.add(JLabel("Plugin Name:"), constraints)

        constraints.gridx = 1
        nameField = JTextField()
        nameField.text = "my-astrbot-plugin"
        panel.add(nameField, constraints)

        // Description
        constraints.gridy = 1
        constraints.gridx = 0
        panel.add(JLabel("Description:"), constraints)

        constraints.gridx = 1
        descriptionField = JTextField()
        descriptionField.text = "My AstrBot plugin"
        panel.add(descriptionField, constraints)

        // Author
        constraints.gridy = 2
        constraints.gridx = 0
        panel.add(JLabel("Author:"), constraints)

        constraints.gridx = 1
        authorField = JTextField()
        authorField.text = System.getProperty("user.name")
        panel.add(authorField, constraints)

        return panel
    }

    override fun doOKAction() {
        val name = nameField.text.trim()
        val description = descriptionField.text.trim()
        val author = authorField.text.trim()

        if (name.isEmpty()) {
            Messages.showErrorDialog(project, "Plugin name cannot be empty", "Error")
            return
        }

        generatePlugin(name, description, author)
        super.doOKAction()
    }

    private fun generatePlugin(name: String, description: String, author: String) {
        ApplicationManager.getApplication().executeOnPooledThread {
            try {
                val projectDir = project.basePath ?: return@executeOnPooledThread
                val pluginDir = "$projectDir/$name"

                // Create plugin directory structure
                java.io.File(pluginDir).mkdirs()
                java.io.File("$pluginDir/handlers").mkdirs()

                // Generate plugin.json
                val pluginJson = """
                    {
                        "id": "${name.lowercase().replace("-", "_")}",
                        "name": "$name",
                        "version": "0.1.0",
                        "description": "$description",
                        "author": "$author",
                        "dependencies": {}
                    }
                """.trimIndent()
                java.io.File("$pluginDir/plugin.json").writeText(pluginJson)

                // Generate __init__.py
                val initPy = """
                    """$name - AstrBot Plugin"""
                    from .plugin import Plugin

                    __all__ = ["Plugin"]
                """.trimIndent()
                java.io.File("$pluginDir/__init__.py").writeText(initPy)

                // Generate plugin.py
                val pluginPy = """
                    """$name - Main plugin class."""
                    from astrbot import Plugin as BasePlugin
                    from astrbot.event import filter, AstrBotMessage

                    class Plugin(BasePlugin):
                        """AstrBot plugin: $name"""

                        async def activate(self):
                            """Called when plugin is activated."""
                            self.logger.info(f"$name plugin activated")

                        async def deactivate(self):
                            """Called when plugin is deactivated."""
                            self.logger.info(f"$name plugin deactivated")

                        @filter.event()
                        async def on_message(self, event: AstrBotMessage):
                            """Handle incoming messages."""
                            pass
                """.trimIndent()
                java.io.File("$pluginDir/plugin.py").writeText(pluginPy)

                // Generate pyproject.toml
                val pyproject = """
                    [project]
                    name = "$name"
                    version = "0.1.0"
                    description = "$description"
                    requires-python = ">=3.10"

                    [project.astrbot-plugin]
                    handler = "$name.plugin:Plugin"
                """.trimIndent()
                java.io.File("$pluginDir/pyproject.toml").writeText(pyproject)

                ApplicationManager.getApplication().invokeLater {
                    Messages.showInfoMessage(
                        project,
                        "Plugin created successfully at: $pluginDir",
                        "Success"
                    )
                }
            } catch (e: Exception) {
                ApplicationManager.getApplication().invokeLater {
                    Messages.showErrorDialog(
                        project,
                        "Failed to create plugin: ${e.message}",
                        "Error"
                    )
                }
            }
        }
    }
}
