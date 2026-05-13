package com.astrbot.ide

import com.intellij.openapi.actionSystem.*
import com.intellij.openapi.project.*
import com.intellij.openapi.ui.*
import com.intellij.openapi.wm.*
import com.intellij.ui.components.*
import com.intellij.util.ui.*
import java.awt.*
import javax.swing.*

class AstrBotPlugin : ProjectManagerListener {
    override fun projectOpened(project: Project) {
        val toolWindow = ToolWindowManager.getInstance(project).getToolWindow("AstrBot Buddy")
        toolWindow?.setAvailable(true)
    }
}

class AstrBotBuddyToolWindowFactory : ToolWindowFactory {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val content = toolWindow.contentManager.factory.createContent(
            AstrBotBuddyPanel(project).getPanel(),
            "AstrBot Status",
            false
        )
        toolWindow.contentManager.addContent(content)
    }

    override fun shouldBeAvailable(project: Project): Boolean = true
}

class AstrBotBuddyPanel(private val project: Project) {
    private lateinit var statusLabel: JLabel
    private lateinit var versionLabel: JLabel
    private lateinit var uptimeLabel: JLabel
    private lateinit var agentListModel: DefaultListModel<String>
    private lateinit var pluginListModel: DefaultListModel<String>
    private lateinit var refreshButton: JButton

    private val apiClient = AstrBotApiClient()

    fun getPanel(): JPanel {
        val panel = JPanel(BorderLayout())

        // Header
        val header = JPanel(BorderLayout())
        header.background = Color(0x2b, 0x2b, 0x2b)
        val titleLabel = JLabel("AstrBot Buddy")
        titleLabel.font = Font("SansSerif", Font.BOLD, 16)
        titleLabel.foreground = Color.WHITE
        header.add(titleLabel, BorderLayout.WEST)

        refreshButton = JButton("Refresh")
        refreshButton.addActionListener { refreshStatus() }
        header.add(refreshButton, BorderLayout.EAST)
        panel.add(header, BorderLayout.NORTH)

        // Main content
        val content = JPanel()
        content.layout = BoxLayout(content, BoxLayout.Y_AXIS)
        content.border = EmptyBorder(10, 10, 10, 10)

        // Status Section
        val statusPanel = JPanel()
        statusPanel.layout = BoxLayout(statusPanel, BoxLayout.Y_AXIS)
        statusPanel.add(JLabel("Status").apply {
            font = font.deriveFont(Font.BOLD, 14f)
        })

        val statusGrid = JPanel(GridLayout(0, 2, 5, 5))
        statusGrid.add(JLabel("Version:"))
        versionLabel = JLabel("Connecting...")
        statusGrid.add(versionLabel)
        statusGrid.add(JLabel("Uptime:"))
        uptimeLabel = JLabel("--")
        statusGrid.add(uptimeLabel)
        statusPanel.add(statusGrid)
        content.add(statusPanel)
        content.add(Box.createVerticalStrut(15))

        // Agents Section
        val agentsPanel = JPanel()
        agentsPanel.layout = BoxLayout(agentsPanel, BoxLayout.Y_AXIS)
        agentsPanel.add(JLabel("Agents").apply {
            font = font.deriveFont(Font.BOLD, 14f)
        })
        agentListModel = DefaultListModel()
        val agentList = JList(agentListModel)
        agentList.visibleRowCount = 5
        agentsPanel.add(JScrollPane(agentList))
        content.add(agentsPanel)
        content.add(Box.createVerticalStrut(15))

        // Plugins Section
        val pluginsPanel = JPanel()
        pluginsPanel.layout = BoxLayout(pluginsPanel, BoxLayout.Y_AXIS)
        pluginsPanel.add(JLabel("Plugins").apply {
            font = font.deriveFont(Font.BOLD, 14f)
        })
        pluginListModel = DefaultListModel()
        val pluginList = JList(pluginListModel)
        pluginList.visibleRowCount = 5
        pluginsPanel.add(JScrollPane(pluginList))
        content.add(pluginsPanel)

        panel.add(JScrollPane(content), BorderLayout.CENTER)

        refreshStatus()
        return panel
    }

    private fun refreshStatus() {
        refreshButton.isEnabled = false
        refreshButton.text = "Refreshing..."

        // Fetch data in background
        Thread {
            try {
                val status = apiClient.getStatus()
                val agents = apiClient.getAgents() ?: emptyList()
                val plugins = apiClient.getPlugins() ?: emptyList()

                // Update UI on EDT
                SwingUtilities.invokeLater {
                    updateUI(status, agents, plugins)
                    refreshButton.isEnabled = true
                    refreshButton.text = "Refresh"
                }
            } catch (e: Exception) {
                SwingUtilities.invokeLater {
                    versionLabel.text = "Disconnected"
                    uptimeLabel.text = "--"
                    agentListModel.clear()
                    agentListModel.addElement("Error: ${e.message}")
                    pluginListModel.clear()
                    refreshButton.isEnabled = true
                    refreshButton.text = "Refresh"
                }
            }
        }.start()
    }

    private fun updateUI(
        status: AstrBotStatus?,
        agents: List<AgentInfo>,
        plugins: List<PluginInfo>
    ) {
        if (status != null) {
            versionLabel.text = status.bot_version
            uptimeLabel.text = formatUptime(status.uptime)
        } else {
            versionLabel.text = "Unknown"
            uptimeLabel.text = "--"
        }

        agentListModel.clear()
        if (agents.isEmpty()) {
            agentListModel.addElement("No agents available")
        } else {
            agents.forEach { agent ->
                val statusIcon = if (agent.status == "active") "●" else "○"
                agentListModel.addElement("$statusIcon ${agent.name} (${agent.type})")
            }
        }

        pluginListModel.clear()
        if (plugins.isEmpty()) {
            pluginListModel.addElement("No plugins installed")
        } else {
            plugins.forEach { plugin ->
                pluginListModel.addElement("${plugin.name} v${plugin.version}")
            }
        }
    }

    private fun formatUptime(seconds: Long): String {
        val hours = seconds / 3600
        val minutes = (seconds % 3600) / 60
        return if (hours > 0) "${hours}h ${minutes}m" else "${minutes}m"
    }
}
