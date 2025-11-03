package com.example.myapplication

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import android.content.Intent

class MainActivity : AppCompatActivity() {
    private lateinit var loginEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var enterButton: Button
    private lateinit var registerButton: Button
    private val BASE_URL = "http://10.0.2.2:8000"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        loginEditText = findViewById(R.id.login)
        passwordEditText = findViewById(R.id.editTextTextPassword)
        enterButton = findViewById(R.id.enter)
        registerButton = findViewById(R.id.register)

        enterButton.setOnClickListener { loginUser() }
        registerButton.setOnClickListener {
            startActivity(Intent(this, reg::class.java))
        }
    }

    private fun loginUser() {
        val login = loginEditText.text.toString().trim()
        val password = passwordEditText.text.toString().trim()

        if (login.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Заполните все поля", Toast.LENGTH_SHORT).show()
            return
        }

        // Преобразуем пароль в число
        val passwordInt = try {
            password.toInt()
        } catch (e: NumberFormatException) {
            Toast.makeText(this, "Пароль должен быть числом", Toast.LENGTH_SHORT).show()
            return
        }

        Thread {
            try {
                val url = URL("$BASE_URL/login")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true

                val jsonObject = JSONObject()
                jsonObject.put("login", login)
                jsonObject.put("password", passwordInt) // отправляем как число

                connection.outputStream.use { os ->
                    os.write(jsonObject.toString().toByteArray())
                }

                val response = connection.inputStream.bufferedReader().use { it.readText() }

                runOnUiThread {
                    handleLoginResponse(response)
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "Ошибка сети", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

    private fun handleLoginResponse(response: String) {
        try {
            val jsonResponse = JSONObject(response)
            val status = jsonResponse.getString("status")

            if (status == "success") {
                val userName = jsonResponse.getString("user_name")
                Toast.makeText(this, "Добро пожаловать, $userName", Toast.LENGTH_LONG).show()
            } else {
                val message = jsonResponse.getString("message")
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Ошибка сервера", Toast.LENGTH_SHORT).show()
        }
    }
}
