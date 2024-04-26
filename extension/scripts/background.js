chrome.runtime.onInstalled.addListener(() =>  {
    console.log("Installed properly...");
});

chrome.runtime.onMessage.addListener(async (message, sender) => {
    console.log("Started listening");
    if (message.from === 'content_script') {
        if (message.action === 'fill_available') {
            chrome.action.show(sender.tab.id);
        }
    } else if (message.from === 'popup') {
        if (message.action === 'do_fill') {
            const url = new URL(message.tab.url);
            const user = message.user
            try {
                const reply = await chrome.runtime.sendNativeMessage('com.pass.drive',
                {
                    type: 'autofill_request',
                    host: url.host,
                    user: user
                });
                if (reply.type === 'autofill_response') {
                    console.log("sending query!")
                    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                        console.log("Entered query!", tabs[0].id)
                        chrome.tabs.sendMessage(tabs[0].id, {action: 'autofill', username: reply.user, password: reply.pass});
                    });
                    
                }
                console.log("Done filling!!")
            } catch (error) {
                console.error('Error communicating:', error);
            }
        }
    }
    return true
});
