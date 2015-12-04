function SendData(data) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'target_value=' + encodeURIComponent(data.target_value) +
               '&kpi_code=' + encodeURIComponent(data.kpi_code) +
               '&period_code=' + encodeURIComponent(data.period_code);
    xhr.open('POST', '/kpi/savestage2', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        //alert( xhr.status + ': ' + xhr.statusText);
        console.log(xhr.status + ': ' + xhr.statusText);
        var e = document.getElementById('tr_'+data.period_code);
        e.className = e.className.replace('', 'danger');
      } else {
        //alert(xhr.responseText);
        //console.log(xhr.responseText);
        //console.log(document.getElementById('save_alert').className);
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));
        var e = document.getElementById('tr_'+data.period_code);
        e.className = e.className.replace('', 'success');
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));

      }
    }
    xhr.send(body);
    return xhr.responseText;
};

function SendTargetValue(pcode) {
    var e = document.getElementById(pcode);

    var data = {
        kpi_code: document.getElementById('kpi_code').value,
        period_code: pcode,
        target_value: e.value
        };
    SendData(data);

};

function ChangeColor(data) {
    var e = document.getElementById('tr_'+data);
    e.className = e.className.replace('success', '');
};
