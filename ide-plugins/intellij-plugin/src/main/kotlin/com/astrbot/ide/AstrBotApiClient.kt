package com.astrbot.ide

import okhttp3.*
import com.google.gson.Gson
import java.io.IOException

/**
 * AstrBot API Client for IntelliJ Plugin
 * Connects to AstrBot server to fetch status, agents, plugins
 */
class AstrBotApiClient(
    private val baseUrl: String = "http://localhost:8000",
    private val apiKey: String = ""
) {
    private val client = OkHttpClient()
    private val gson = Gson()

    private val jsonMediaType = MediaType.get("application/json; charset=utf-8")

    fun getStatus(): AstrBotStatus? {
        val request = Request.Builder()
            .url("$baseUrl/api/status")
            .apply {
                if (apiKey.isNotEmpty()) {
                    addHeader("Authorization", "Bearer $apiKey")
                }
            }
            .build()

        return executeRequest(request) { response ->
            gson.fromJson(response.body?.string(), AstrBotStatus::class.java)
        }
    }

    fun getAgents(): List<AgentInfo>? {
        val request = Request.Builder()
            .url("$baseUrl/api/agents")
            .apply {
                if (apiKey.isNotEmpty()) {
                    addHeader("Authorization", "Bearer $apiKey")
                }
            }
            .build()

        return executeRequest(request) { response ->
            val type = object : com.google.gson.reflect.TypeToken<List<AgentInfo>>() {}.type
            gson.fromJson(response.body?.string(), type)
        }
    }

    fun getPlugins(): List<PluginInfo>? {
        val request = Request.Builder()
            .url("$baseUrl/api/plugins")
            .apply {
                if (apiKey.isNotEmpty()) {
                    addHeader("Authorization", "Bearer $apiKey")
                }
            }
            .build()

        return executeRequest(request) { response ->
            val type = object : com.google.gson.reflect.TypeToken<List<PluginInfo>>() {}.type
            gson.fromJson(response.body?.string(), type)
        }
    }

    fun callAgent(agentId: String, input: String): String? {
        val jsonBody = """{"input": "$input"}"""
        val requestBody = RequestBody.create(jsonMediaType, jsonBody)

        val request = Request.Builder()
            .url("$baseUrl/api/agents/$agentId/call")
            .post(requestBody)
            .apply {
                if (apiKey.isNotEmpty()) {
                    addHeader("Authorization", "Bearer $apiKey")
                }
            }
            .build()

        return executeRequest(request) { response ->
            val result = gson.fromJson(response.body?.string(), Map::class.java)
            result["response"] as? String
        }
    }

    fun installPlugin(pluginId: String): Boolean {
        val jsonBody = """{"plugin_id": "$pluginId"}"""
        val requestBody = RequestBody.create(jsonMediaType, jsonBody)

        val request = Request.Builder()
            .url("$baseUrl/api/plugins/install")
            .post(requestBody)
            .apply {
                if (apiKey.isNotEmpty()) {
                    addHeader("Authorization", "Bearer $apiKey")
                }
            }
            .build()

        return executeRequest(request) { true }
    }

    private fun <T> executeRequest(request: Request, parser: (Response) -> T): T? {
        return try {
            client.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    parser(response)
                } else {
                    null
                }
            }
        } catch (e: IOException) {
            null
        }
    }
}

// Data classes
data class AstrBotStatus(
    val bot_version: String = "unknown",
    val agents: Int = 0,
    val plugins: Int = 0,
    val memory_usage: Long = 0,
    val uptime: Long = 0
)

data class AgentInfo(
    val id: String,
    val name: String,
    val status: String,
    val type: String = "conversational"
)

data class PluginInfo(
    val id: String,
    val name: String,
    val version: String,
    val author: String = "",
    val description: String = ""
)
