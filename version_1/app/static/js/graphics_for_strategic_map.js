var draw_goals = {};

(function() {
    var canvas = this.__canvas = new fabric.Canvas('graph_map');
    fabric.Object.prototype.transparentCorners = false;
    var top_start = 200;
    var left_start = 30;
    var line_color = '#eee';
    var radius = 65;

    canvas.add(new fabric.Line([0, top_start,800, top_start], {
        fill: '#eee',
        stroke: '#eee',
        strokeWidth: 2,
        selectable: false
    }));
    canvas.add(new fabric.Line([0, top_start*2,800, top_start*2], {
        fill: '#eee',
        stroke: '#eee',
        strokeWidth: 2,
        selectable: false
    }));
    canvas.add(new fabric.Line([0, top_start*3,800, top_start*3], {
        fill: '#eee',
        stroke: '#eee',
        strokeWidth: 2,
        selectable: false
    }));
    canvas.add(new fabric.Line([0, top_start*4,800,top_start*4], {
        fill: '#eee',
        stroke: '#eee',
        strokeWidth: 2,
        selectable: false
    }));

    var text_options = {
        fill: '#eee',
        fontSize: 20,
        fontFamily: 'Arial',
        textAlign: 'center',
        fontWeight: 'bold',
        angle: -90,
        left: 0,
        top: top_start - top_start*0.2
    };

    canvas.add(new fabric.Text('Финансы', text_options));
    text_options.top = top_start*2 - top_start*0.2;
    canvas.add(new fabric.Text('Клиенты', text_options));
    text_options.top = top_start*3 - top_start*0.2;
    canvas.add(new fabric.Text('Процессы', text_options));
    text_options.top = top_start*4 - top_start*0.2;
    canvas.add(new fabric.Text('Персонал', text_options));

    var original_color = 'red';
    var original_text_color = '#ffffff'

    canvas.on('mouse:over', function(e) {
        if (e.target instanceof fabric.Group) {
            original_color = e.target.getFill();
            original_text_color = e.target.item(1).getFill();
            //console.log(e.target);
            e.target.setFill('#eee');
            e.target.item(1).setFill('#000000');
        }
        canvas.renderAll();
    });

    canvas.on('mouse:out', function(e) {
        if (e.target instanceof fabric.Group) {
            e.target.setFill(original_color);
            e.target.item(1).setFill(original_text_color);
        }
        canvas.renderAll();
    });

    canvas.on('object:moving', function(e) {
        var p = e.target;
        draw_data[p.code].left = p.left;
        draw_data[p.code].top = p.top;
        for (var i = 0; i < p.in_lines.length; i++) {
            p.in_lines[i] && p.in_lines[i].set({ 'x2': p.left + p.width/2, 'y2': p.top + p.height/2 });
        };
        for (var i = 0; i < p.out_lines.length; i++) {
            p.out_lines[i] && p.out_lines[i].set({ 'x1': p.left + p.width/2, 'y1': p.top + p.height/2 });
        };

        //console.log(p.code, p.centerX, p.centerY);


        canvas.renderAll();
    });

    //console.log(goals_in_json);
    //var goals = JSON.parse(goals_in_json);
    var goals = goals_in_json;

    var linked_goals = JSON.parse(linked_goals_in_json);
    //console.log(draw_data);

    //for (var key in goals) {
    //  console.log(goals[key].code, goals[key].perspective, goals[key].name);
    //};


    var i = f = c = p = h = 0;

    for (var key in goals) {
        if (goals[key].perspective == 0) {
        // если перспектива финансы
            var klass = 'Rect';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  rx: 5,
                  width: 2*radius,
                  height: radius,
                  fill: financial_map_color
            };
            var group_options = {
              left: left_start + f*120,
              top: 10
            }
            f++
        }
        else if (goals[key].perspective == 1) {
        // если перспектива клиенты
            var klass = 'Rect';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  rx: 5,
                  width: 2*radius,
                  height: radius,
                  fill: client_map_color
            };
            var group_options = {
              left: left_start + c*140,
              top: top_start + 30
            }
            c++
        }
        else if (goals[key].perspective == 2) {
        // если перспектива процессы
            var klass = 'Rect';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  rx: 5,
                  width: 2*radius,
                  height: radius,
                  fill: process_map_color
            };
            var group_options = {
              left: left_start + p*120,
              top: top_start*2 + 30
            }
            p++
        }
        else if (goals[key].perspective == 3) {
        // если перспектива персонал
            var klass = 'Rect';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  rx: 5,
                  width: 2*radius,
                  height: radius,
                  fill: hr_map_color
            };
            var group_options = {
              left: left_start + h*120,
              top: top_start*3 + 30
            }
            h++
        }
        else {
        // если перспектива не определена
            var klass = 'Rect';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  rx: 5,
                  width: 2*radius,
                  height: radius,
                  fill: '#eee'
            };
            var group_options = {
              left: left_start + i*120,
              top: top_start*4 + 30
            }
            i++
        }

        var goal = new fabric[klass](options);

        //console.log(key, goals[key].name)
        goals_name = goals[key].name;
        var j = i = 0;
        text = goals_name.replace(/\s/g, function(str, offset, s) {
          //console.log(offset/8, Math.floor(offset/8));
          //if ((offset/8 - Math.floor(offset/8)) < 0.20) {
          //console.log(j ,offset);
          j = j + (offset - i);
          i = offset;
          if (j < 8) {
            //console.log('Печатаем пробел');
            return(' ');
            }
          else {
            //console.log('Печатаем перенос');
            j = 0;
            return '\n';
            }
          })
        //console.log(goals_name, text)

        var text_options1 = {
            fill: '#fff',
            fontSize: 11,
            fontFamily: 'Arial',
            originX: 'center',
            originY: 'center',
            textAlign: 'center'
        };

        var text = new fabric.Text(text, text_options1);

        var group = new fabric.Group([ goal, text ], group_options);
        group.hasControls = group.hasBorders = false;
        group.code =  goals[key].code;
        group.in_lines = [];
        group.out_lines = [];
        draw_goals[key] = group;
        if (draw_data[key]) {
            group.left = draw_data[key].left;
            group.top = draw_data[key].top;
        }
        else {
            draw_data[key] = {
                left: group.left,
                top: group.top
            };
        }
        group.centerX = group.left + group.width/2;
        group.centerY = group.top + group.height/2;
        //console.log(group.code, group.centerX, group.centerY);
        canvas.add(group);

      };

    for (var x in draw_goals){
        //console.log('Для цели: ', draw_goals[x].code);
        //console.log('Координаты: ', draw_goals[x].centerX, draw_goals[x].centerY);

        for (var y in linked_goals[x]){
            yy = linked_goals[x][y];
            if (yy in draw_goals){
                //console.log('Связанная цель: ', yy);
                //console.log('Координаты: ', draw_goals[yy].centerX, draw_goals[yy].centerY);
                var line = makeLine([ draw_goals[x].centerX, draw_goals[x].centerY,
                draw_goals[yy].centerX, draw_goals[yy].centerY ]);
                canvas.add(line);
                draw_goals[x].out_lines.push(line);
                draw_goals[yy].in_lines.push(line);
                canvas.sendToBack(line);
            }
        }
    }

    function makeLine(coords) {
        return new fabric.Line(coords, {
            fill: line_color,
            stroke: line_color,
            strokeWidth: 2,
            selectable: false
        });
    }

    //console.log(draw_data);

})();

function sendDrawData(data) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'json_string=' + encodeURIComponent(JSON.stringify(data)) + '&map_code=' + encodeURIComponent(map_code);
    xhr.open('POST', '/save_map_draw', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        alert(xhr.status + ': ' + xhr.statusText);
      } else {
        alert(xhr.responseText);
      }
    }
    xhr.send(body);
};

var download_button = document.getElementById('download_draw');

function SaveDraw() {
    var canvas = document.getElementById('graph_map');
    var dataURL = canvas.toDataURL('image/png');
    download_button.href = dataURL;
};