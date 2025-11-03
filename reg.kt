package com.example.myapplication

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class reg : AppCompatActivity() {
    private lateinit var surnameEditText: EditText
    private lateinit var nameEditText: EditText
    private lateinit var lastnameEditText: EditText
    private lateinit var passportEditText: EditText
    private lateinit var loginEditText: EditText
    private lateinit var passwordEditText: EditText
    private lateinit var regButton: Button
    private lateinit var backButton: Button
    private val BASE_URL = "http://10.0.2.2:8000"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_reg)

        surnameEditText = findViewById(R.id.surname)
        nameEditText = findViewById(R.id.name)
        lastnameEditText = findViewById(R.id.lastdname)
        passportEditText = findViewById(R.id.passport)
        loginEditText = findViewById(R.id.login)
        passwordEditText = findViewById(R.id.editTextTextPassword)
        regButton = findViewById(R.id.reg_button)
        backButton = findViewById(R.id.back)

        regButton.setOnClickListener { registerUser() }
        backButton.setOnClickListener { finish() }
    }

    private fun registerUser() {
        val surname = surnameEditText.text.toString().trim()
        val name = nameEditText.text.toString().trim()
        val lastname = lastnameEditText.text.toString().trim()
        val passport = passportEditText.text.toString().trim()
        val login = loginEditText.text.toString().trim()
        val password = passwordEditText.text.toString().trim()

        if (surname.isEmpty() || name.isEmpty() || lastname.isEmpty() ||
            passport.isEmpty() || login.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Заполните все поля", Toast.LENGTH_SHORT).show()
            return
        }

        // Преобразуем в числа
        val passportInt = try {
            passport.toInt()
        } catch (e: NumberFormatException) {
            Toast.makeText(this, "Паспорт должен быть числом", Toast.LENGTH_SHORT).show()
            return
        }

        val passwordInt = try {
            password.toInt()
        } catch (e: NumberFormatException) {
            Toast.makeText(this, "Пароль должен быть числом", Toast.LENGTH_SHORT).show()
            return
        }

        Thread {
            try {
                val url = URL("$BASE_URL/register")
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true

                val jsonObject = JSONObject()
                jsonObject.put("name", name)
                jsonObject.put("surname", surname)
                jsonObject.put("lastname", lastname)
                jsonObject.put("passport", passportInt) // число
                jsonObject.put("login", login)
                jsonObject.put("password", passwordInt) // число

                connection.outputStream.use { os ->
                    os.write(jsonObject.toString().toByteArray())
                }

                val response = connection.inputStream.bufferedReader().use { it.readText() }

                runOnUiThread {
                    handleRegisterResponse(response)
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "Ошибка сети", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }

    private fun handleRegisterResponse(response: String) {
        try {
            val jsonResponse = JSONObject(response)
            val status = jsonResponse.getString("status")
            val message = jsonResponse.getString("message")

            if (status == "success") {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
                finish()
            } else {
                Toast.makeText(this, message, Toast.LENGTH_LONG).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Ошибка сервера", Toast.LENGTH_SHORT).show()
        }
    }
}