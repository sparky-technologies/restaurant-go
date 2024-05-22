# restaurant-go
Food Market plate

# To verify that Simple JWT is working, you can use curl to issue a couple of test requests:

```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "passord"}' \
  http://localhost:8000/api/token/

...
{
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNjIwMjkzOCwiaWF0IjoxNzE2MTE2NTM4LCJqdGkiOiI1MDRiMTcyNGI0N2U0YjMwYjhiNzMzY2UyZGQ4ZmIzMSIsInVzZXJfaWQiOjF9.8jpuoUPzmAVMqtRLdBbdMuVz6zP2RNx9GBiQq8YVObc","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MTE2ODM4LCJpYXQiOjE3MTYxMTY1MzgsImp0aSI6IjMyOTQ0NjM3N2Y5YzQwMGNiZWJkN2ZkYjE4MjAzNzIxIiwidXNlcl9pZCI6MX0.9pJGXzUB_2BrnR24YIV7sgi2xl8xRT3Aw8hOG8IVz2k"
}
```
