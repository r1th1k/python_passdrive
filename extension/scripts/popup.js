(function () {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        var tab = tabs[0];

        var url = new URL(tab.url);

        document.getElementById('host').textContent = url.host;

        document.getElementById('button-fill').addEventListener('click', function () {
            document.getElementById('progress-indeterminate').style.display = 'block';
            const user = document.getElementById("user");
            console.log(user.value);
            chrome.runtime.sendMessage('', {
                from: 'popup',
                action: 'do_fill',
                tab: tab,
                user: user.value
            }, function (reply) {
                document.getElementById('progress-indeterminate').style.display = 'none';
            });
        });
    });
})();