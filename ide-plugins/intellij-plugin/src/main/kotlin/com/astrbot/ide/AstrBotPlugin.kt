package com.astrbot.ide

import com.intellij.openapi.actionSystem.*
import com.intellij.openapi.project.*
import com.intellij.openapi.ui.*
import com.intellij.openapi.wm.*
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
    private lateinit var agentListModel: DefaultListModel<String>
    private lateinit var pluginListModel: DefaultListModel<String>

    fun getPanel(): JPanel {
        val panel = JPanel()
        panel.layout = BoxLayout(panel, BoxLayout.Y_AXIS)

        // Status Section
        panel.add(JLabel("AstrBot Status").apply { font = it.font.deriveFont(16f) })
        statusLabel = JLabel("Connecting...")
        panel.add(statusLabel)
        panel.add(Box.createVerticalStrut(10))

        // Agents Section
        panel.add(JLabel("Agents").apply { font = it.font.deriveFont(14f) })
        agentListModel = DefaultListModel()
        panel.add(JList(agentListModel))
        panel.add(Box.createVerticalStrut(10))

        // Plugins Section
        panel.add(JLabel("Plugins").apply { font = it.font.deriveFont(14f) })
        pluginListModel = DefaultListModel()
        panel.add(JList(pluginListModel))

        // Refresh button
        val refreshButton = JButton("Refresh")
        refreshButton.addActionListener { refreshStatus() }
        panel.add(Box.createVerticalStrut(10))
        panel.add(refreshButton)

        refreshStatus()
        return panel
    }

    private fun refreshStatus() {
        // TODO: Connect to AstrBot API
        statusLabel.text = "Version: 1.0.0 | Uptime: --"
        agentListModel.clear()
        agentListModel.addElement("Connect to AstrBot to view agents")
        pluginListModel.clear()
        pluginListModel.addElement("Connect to AstrBot to view plugins")
    }
}
