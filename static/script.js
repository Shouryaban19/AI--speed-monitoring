function fetchLogs() {
    fetch('/get_logs')
        .then(res => res.json())
        .then(data => {
            const box = document.getElementById("logBox");
            box.innerHTML = data.join("<br>");
            box.scrollTop = box.scrollHeight;
        });
}

setInterval(fetchLogs, 1000);