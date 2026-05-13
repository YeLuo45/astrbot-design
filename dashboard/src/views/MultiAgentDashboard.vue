<template>
  <div class="multi-agent-dashboard">
    <div class="dashboard-header">
      <h1>Multi-Agent Dashboard</h1>
      <div class="header-actions">
        <button @click="refreshStatus" class="refresh-btn">
          {{ refreshing ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Team Selection -->
    <div class="team-section">
      <h2>Select Team</h2>
      <div class="team-cards">
        <div
          v-for="team in availableTeams"
          :key="team.id"
          class="team-card"
          :class="{ active: selectedTeam === team.id }"
          @click="selectTeam(team.id)"
        >
          <h3>{{ team.name }}</h3>
          <p>{{ team.description }}</p>
          <div class="agent-list">
            <span v-for="agent in team.agents" :key="agent" class="agent-badge">
              {{ agent }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Input -->
    <div class="task-section">
      <h2>Execute Task</h2>
      <div class="task-input">
        <select v-model="selectedTeam" class="team-select">
          <option value="">Select a team...</option>
          <option v-for="team in availableTeams" :key="team.id" :value="team.id">
            {{ team.name }}
          </option>
        </select>
        <textarea
          v-model="taskDescription"
          placeholder="Enter task description..."
          class="task-textarea"
          rows="3"
        ></textarea>
        <button @click="executeTask" :disabled="!canExecute" class="execute-btn">
          Execute
        </button>
      </div>
    </div>

    <!-- Active Tasks -->
    <div class="tasks-section">
      <h2>Active Tasks</h2>
      <div v-if="activeTasks.length === 0" class="no-tasks">
        No active tasks
      </div>
      <div v-else class="task-list">
        <div v-for="task in activeTasks" :key="task.task_id" class="task-item">
          <div class="task-header">
            <span class="task-id">{{ task.task_id.substring(0, 8) }}...</span>
            <span class="task-status" :class="task.status">{{ task.status }}</span>
          </div>
          <div class="task-body">
            <p class="task-description">{{ task.task }}</p>
            <div class="task-meta">
              <span>Team: {{ task.team }}</span>
            </div>
          </div>
          <div class="task-actions">
            <button @click="viewStatus(task.task_id)" class="action-btn">Status</button>
            <button @click="viewMemory(task.task_id)" class="action-btn">Memory</button>
            <button @click="cancelTask(task.task_id)" class="action-btn cancel">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Graph Visualization -->
    <div class="graph-section">
      <h2>Task Graph</h2>
      <div class="graph-container">
        <svg :viewBox="`0 0 ${graphWidth} ${graphHeight}`" class="task-graph">
          <!-- Nodes -->
          <g v-for="node in graphNodes" :key="node.id">
            <circle
              :cx="node.x"
              :cy="node.y"
              :r="nodeRadius"
              :class="['graph-node', node.type, node.status]"
            />
            <text
              :x="node.x"
              :y="node.y + nodeRadius + 15"
              class="graph-label"
            >
              {{ node.label }}
            </text>
          </g>
          <!-- Edges -->
          <line
            v-for="edge in graphEdges"
            :key="`${edge.from}-${edge.to}`"
            :x1="edge.x1"
            :y1="edge.y1"
            :x2="edge.x2"
            :y2="edge.y2"
            class="graph-edge"
          />
        </svg>
      </div>
    </div>

    <!-- Agent Status Monitor -->
    <div class="agents-section">
      <h2>Agent Status</h2>
      <div class="agents-grid">
        <div v-for="agent in agentStatuses" :key="agent.agent_id" class="agent-status-card">
          <div class="agent-header">
            <span class="agent-name">{{ agent.name }}</span>
            <span class="agent-indicator" :class="{ active: agent.running }"></span>
          </div>
          <div class="agent-details">
            <p><strong>ID:</strong> {{ agent.agent_id }}</p>
            <p><strong>Domain:</strong> {{ agent.domain || 'N/A' }}</p>
            <p><strong>Queue:</strong> {{ agent.queue_size }} messages</p>
            <p v-if="agent.current_tasks"><strong>Tasks:</strong> {{ agent.current_tasks.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Flow -->
    <div class="messages-section">
      <h2>Message Flow</h2>
      <div class="message-log">
        <div v-if="messages.length === 0" class="no-messages">
          No messages yet
        </div>
        <div v-else class="message-list">
          <div
            v-for="msg in displayedMessages"
            :key="msg.id"
            class="message-item"
            :class="msg.type"
          >
            <span class="msg-time">{{ formatTime(msg.timestamp) }}</span>
            <span class="msg-sender">{{ msg.sender }}</span>
            <span class="msg-arrow">→</span>
            <span class="msg-recipient">{{ msg.recipient || 'broadcast' }}</span>
            <span class="msg-type">[{{ msg.type }}]</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Detail Modal -->
    <div v-if="selectedTaskDetail" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h3>Task Details</h3>
        <pre>{{ JSON.stringify(selectedTaskDetail, null, 2) }}</pre>
        <button @click="closeModal" class="close-btn">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const API_BASE = '/api/multi-agent'

export default {
  name: 'MultiAgentDashboard',
  
  setup() {
    const availableTeams = ref([
      {
        id: 'code-review',
        name: 'Code Review Team',
        description: 'Code generation, review, and quality critique',
        agents: ['coordinator', 'code-generator', 'code-reviewer', 'code-critic']
      },
      {
        id: 'research',
        name: 'Research Team',
        description: 'Web search, document analysis, and synthesis',
        agents: ['coordinator', 'web-searcher', 'doc-analyzer', 'synthesizer']
      },
      {
        id: 'debate',
        name: 'Debate Team',
        description: 'Pro/con arguments with judge',
        agents: ['coordinator', 'pro-arguer', 'con-arguer', 'debate-judge']
      }
    ])

    const selectedTeam = ref('')
    const taskDescription = ref('')
    const activeTasks = ref([])
    const agentStatuses = ref([])
    const messages = ref([])
    const selectedTaskDetail = ref(null)
    const refreshing = ref(false)
    const graphWidth = 800
    const graphHeight = 400
    const nodeRadius = 30

    let pollInterval = null

    const canExecute = computed(() => {
      return selectedTeam.value && taskDescription.value.trim()
    })

    const graphNodes = computed(() => {
      // Generate nodes from tasks
      const nodes = []
      let index = 0
      activeTasks.value.forEach((task, taskIndex) => {
        const x = 100 + (taskIndex % 3) * 200
        const y = 100
        nodes.push({
          id: task.task_id,
          label: task.team,
          x,
          y,
          type: 'task',
          status: task.status
        })
        index++
      })
      return nodes
    })

    const graphEdges = computed(() => {
      // Generate edges between nodes
      const edges = []
      for (let i = 0; i < graphNodes.value.length - 1; i++) {
        const from = graphNodes.value[i]
        const to = graphNodes.value[i + 1]
        edges.push({
          from: from.id,
          to: to.id,
          x1: from.x,
          y1: from.y + nodeRadius,
          x2: to.x,
          y2: to.y - nodeRadius
        })
      }
      return edges
    })

    const displayedMessages = computed(() => {
      return messages.value.slice(-20)
    })

    const selectTeam = (teamId) => {
      selectedTeam.value = teamId
    }

    const executeTask = async () => {
      if (!canExecute.value) return

      try {
        const response = await fetch(`${API_BASE}/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            team: selectedTeam.value,
            task: taskDescription.value
          })
        })
        const data = await response.json()
        
        activeTasks.value.push({
          task_id: data.task_id,
          team: data.team,
          task: taskDescription.value,
          status: 'running'
        })

        taskDescription.value = ''
      } catch (error) {
        console.error('Failed to execute task:', error)
      }
    }

    const refreshStatus = async () => {
      refreshing.value = true
      try {
        // Refresh all active tasks
        for (const task of activeTasks.value) {
          await viewStatus(task.task_id)
        }
      } finally {
        refreshing.value = false
      }
    }

    const viewStatus = async (taskId) => {
      try {
        const response = await fetch(`${API_BASE}/status/${taskId}`)
        const data = await response.json()
        
        const taskIndex = activeTasks.value.findIndex(t => t.task_id === taskId)
        if (taskIndex >= 0) {
          activeTasks.value[taskIndex].status = data.status
        }
      } catch (error) {
        console.error('Failed to get status:', error)
      }
    }

    const viewMemory = async (taskId) => {
      try {
        const response = await fetch(`${API_BASE}/memory/${taskId}`)
        const data = await response.json()
        selectedTaskDetail.value = data.snapshot
      } catch (error) {
        console.error('Failed to get memory:', error)
      }
    }

    const cancelTask = async (taskId) => {
      try {
        await fetch(`${API_BASE}/task/${taskId}`, { method: 'DELETE' })
        const taskIndex = activeTasks.value.findIndex(t => t.task_id === taskId)
        if (taskIndex >= 0) {
          activeTasks.value.splice(taskIndex, 1)
        }
      } catch (error) {
        console.error('Failed to cancel task:', error)
      }
    }

    const closeModal = () => {
      selectedTaskDetail.value = null
    }

    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString()
    }

    const fetchAgentStatuses = async () => {
      // In a real implementation, this would fetch from an API
      // For now, we'll use static data
      agentStatuses.value = [
        { agent_id: 'coordinator', name: 'Coordinator', running: true, queue_size: 0, domain: null },
        { agent_id: 'code-generator', name: 'CodeGenerator', running: true, queue_size: 0, domain: 'code' },
        { agent_id: 'code-reviewer', name: 'CodeReviewer', running: true, queue_size: 0, domain: 'code-review' },
        { agent_id: 'code-critic', name: 'CodeCritic', running: true, queue_size: 0, domain: 'code-quality' }
      ]
    }

    const addMessage = (msg) => {
      messages.value.push(msg)
      if (messages.value.length > 100) {
        messages.value = messages.value.slice(-100)
      }
    }

    onMounted(() => {
      fetchAgentStatuses()
      // Poll for updates every 5 seconds
      pollInterval = setInterval(refreshStatus, 5000)
    })

    onUnmounted(() => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    })

    return {
      availableTeams,
      selectedTeam,
      taskDescription,
      activeTasks,
      agentStatuses,
      messages,
      selectedTaskDetail,
      refreshing,
      graphWidth,
      graphHeight,
      nodeRadius,
      canExecute,
      graphNodes,
      graphEdges,
      displayedMessages,
      selectTeam,
      executeTask,
      refreshStatus,
      viewStatus,
      viewMemory,
      cancelTask,
      closeModal,
      formatTime
    }
  }
}
</script>

<style scoped>
.multi-agent-dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 28px;
  margin: 0;
}

.refresh-btn {
  padding: 8px 16px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.team-section,
.task-section,
.tasks-section,
.graph-section,
.agents-section,
.messages-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

h2 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

.team-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.team-card {
  padding: 15px;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.team-card:hover {
  border-color: #4a90d9;
}

.team-card.active {
  border-color: #4a90d9;
  background: #e8f4fc;
}

.team-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.team-card p {
  margin: 0 0 10px;
  font-size: 14px;
  color: #666;
}

.agent-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.agent-badge {
  padding: 3px 8px;
  background: #e0e0e0;
  border-radius: 3px;
  font-size: 12px;
}

.task-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.team-select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.task-textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.execute-btn {
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.execute-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.no-tasks {
  padding: 20px;
  text-align: center;
  color: #666;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  background: white;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.task-id {
  font-family: monospace;
  font-size: 12px;
  color: #666;
}

.task-status {
  padding: 3px 10px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: bold;
}

.task-status.running {
  background: #fff3cd;
  color: #856404;
}

.task-status.done {
  background: #d4edda;
  color: #155724;
}

.task-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.task-status.cancelled {
  background: #e2e3e5;
  color: #383d41;
}

.task-description {
  margin: 0 0 10px;
  font-size: 14px;
}

.task-meta {
  font-size: 12px;
  color: #666;
}

.task-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-btn {
  padding: 5px 10px;
  border: 1px solid #ccc;
  background: white;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.action-btn.cancel {
  color: #dc3545;
  border-color: #dc3545;
}

.graph-container {
  background: white;
  border-radius: 6px;
  padding: 10px;
  overflow-x: auto;
}

.task-graph {
  width: 100%;
  height: 300px;
}

.graph-node {
  fill: #4a90d9;
  stroke: #2c5aa0;
  stroke-width: 2;
}

.graph-node.task {
  fill: #4a90d9;
}

.graph-node.result {
  fill: #4CAF50;
}

.graph-node.critique {
  fill: #ff9800;
}

.graph-node.pending {
  fill: #e0e0e0;
}

.graph-node.running {
  fill: #fff3cd;
}

.graph-node.done {
  fill: #d4edda;
}

.graph-node.failed {
  fill: #f8d7da;
}

.graph-label {
  font-size: 10px;
  text-anchor: middle;
}

.graph-edge {
  stroke: #999;
  stroke-width: 1.5;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.agent-status-card {
  background: white;
  padding: 15px;
  border-radius: 6px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.agent-name {
  font-weight: bold;
}

.agent-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;
}

.agent-indicator.active {
  background: #4CAF50;
}

.agent-details p {
  margin: 5px 0;
  font-size: 13px;
}

.no-messages {
  padding: 20px;
  text-align: center;
  color: #666;
}

.message-list {
  max-height: 300px;
  overflow-y: auto;
}

.message-item {
  padding: 8px;
  background: white;
  margin-bottom: 5px;
  border-radius: 3px;
  font-size: 13px;
  font-family: monospace;
}

.message-item.task {
  border-left: 3px solid #4a90d9;
}

.message-item.result {
  border-left: 3px solid #4CAF50;
}

.message-item.critique {
  border-left: 3px solid #ff9800;
}

.msg-time {
  color: #666;
  margin-right: 10px;
}

.msg-sender {
  font-weight: bold;
}

.msg-arrow {
  margin: 0 5px;
  color: #999;
}

.msg-recipient {
  color: #333;
}

.msg-type {
  margin-left: 10px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
}

.close-btn {
  margin-top: 15px;
  padding: 8px 16px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
