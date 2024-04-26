console.log("surprise surpeise")

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    console.log(message)
    if (message.action === 'autofill') {
        var usernameField = document.getElementById('username'); 
        var passwordField = document.getElementById('password'); 

        if (usernameField && passwordField) {
            usernameField.value = message.username;
            passwordField.value = message.password;
        }
    }
});