function set_download_url() {
    let httpRequest = new XMLHttpRequest();
    httpRequest.open('GET', 'https://api.github.com/repos/DancingSnow0517/StarRail-gacha/releases/latest');
    httpRequest.send();
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            let download_url
            if (httpRequest.status === 200) {
                try {
                    let json = JSON.parse(httpRequest.responseText);
                download_url = json.assets[0].browser_download_url;
                } catch (e) {
                    console.log('获得下载链接失败.');
                    download_url = 'https://github.com/DancingSnow0517/StarRail-gacha/releases'
                }

            } else {
                console.log('获得下载链接失败.');
                download_url = 'https://github.com/DancingSnow0517/StarRail-gacha/releases'
            }
            let bt1 = document.getElementById('download_1')
            let bt2 = document.getElementById('download_2')
            bt1.href = download_url
            bt2.href = download_url
        }
    }
}

set_download_url()