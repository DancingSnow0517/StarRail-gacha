function set_download_url() {
    let httpRequest = new XMLHttpRequest();
    httpRequest.open('GET', 'https://api.github.com/repos/DancingSnow0517/StarRail-gacha/releases/latest');
    httpRequest.send();
    httpRequest.onreadystatechange = function () {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            let download_url = 'https://github.com/DancingSnow0517/StarRail-gacha/releases'
            let version_tag = null
            if (httpRequest.status === 200) {
                try {
                    let json = JSON.parse(httpRequest.responseText);
                    download_url = json.assets[0].browser_download_url;
                    version_tag = json.tag_name
                } catch (e) {
                    console.log('获得下载链接失败.');
                }

            } else {
                console.log('获得下载链接失败.');
            }
            let bt1 = document.getElementById('download_1')
            let bt2 = document.getElementById('download_2')
            let backup_download = document.getElementById('backup_download')
            if (version_tag === null) {
                bt2.innerText = '立即下载'
            } else {
                bt2.innerText = '立即下载 v.' + version_tag
                backup_download.className = 'button size-large type-link'
            }
            bt1.href = download_url
            bt2.href = download_url
            backup_download.href = 'https://ghproxy.com/' + download_url
        }
    }
}

set_download_url()