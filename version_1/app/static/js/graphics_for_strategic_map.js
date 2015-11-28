(function() {
    var canvas = this.__canvas = new fabric.Canvas('graph_map');
    fabric.Object.prototype.transparentCorners = false;
    var original_color = 'red';
    var original_text_color = '#ffffff'

    canvas.on('mouse:over', function(e) {
        original_color = e.target.getFill();
        original_text_color = e.target.item(1).getFill();
        console.log(e.target);
        e.target.setFill('#eee');
        e.target.item(1).setFill('#000000');
        canvas.renderAll();
    });

    canvas.on('mouse:out', function(e) {
        e.target.setFill(original_color);
        e.target.item(1).setFill(original_text_color);
        canvas.renderAll();
    });

    var text_options = {
    fill: 'green',
    fontSize: 10,
    fontFamily: 'Arial',
    textAlign: 'center',
    originX: 'center',
    originY: 'center'
    };

    var goals = JSON.parse(goals_in_json);
    //for (var key in goals) {
    //  console.log(goals[key].code, goals[key].perspective, goals[key].name);
    //};


    var i = 0;
    for (var key in goals) {
        if (goals[key].perspective == 0) {
        // если перспектива финансы
            var klass = 'Rect';
            var options = {
                  width: 100,
                  height: 50,
                  originX: 'center',
                  originY: 'center',
                  fill: financial_map_color
            };
            var group_options = {
              left: 0 + i*120,
              top: 10
            }
        }
        else if (goals[key].perspective == 1) {
        // если перспектива клиенты
            var klass = 'Circle';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  radius: 50,
                  scaleY: 0.5,
                  fill: client_map_color
            };
            var group_options = {
              left: 0 + i*120,
              top: 100
            }
        }
        else if (goals[key].perspective == 2) {
        // если перспектива процессы
            var klass = 'Circle';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  radius: 30,
                  fill: process_map_color
            };
            var group_options = {
              left: 0 + i*120,
              top: 200
            }
        }
        else if (goals[key].perspective == 3) {
        // если перспектива персонал
            var klass = 'Circle';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  radius: 30,
                  fill: hr_map_color
            };
            var group_options = {
              left: 0 + i*120,
              top: 300
            }
        }
        else {
        // если перспектива не определена
            var klass = 'Circle';
            var options = {
                  originX: 'center',
                  originY: 'center',
                  radius: 30,
                  fill: '#eee'
            };
            var group_options = {
              left: 0 + i*120,
              top: 400
            }
        }

        var goal = new fabric[klass](options);
        goal.code =  goals[key].code;
        goal.connections = 'Список связей с другими целями.';

        goals_name = goals[key].name
        text = goals_name.replace(/\s/g, function(str, offset, s) {
          //console.log(offset/8, Math.floor(offset/8));
          if ((offset/8 - Math.floor(offset/8)) < 0.20) {
            return(' ');
            }
          else {
            return '\n';
            }
          })
        //console.log(goals_name, text)

        var text_options1 = {
            fill: '#ffffff',
            fontSize: 11,
            fontFamily: 'Arial',
            originX: 'center',
            originY: 'center',
            textAlign: 'center'
        };

        var text = new fabric.Text(text, text_options1);

        var group = new fabric.Group([ goal, text ], group_options);
        canvas.add(group);
        i++;
      };


    function makeLine(coords) {
    return new fabric.Line(coords, {
      fill: 'red',
      stroke: 'red',
      strokeWidth: 5,
      selectable: false
    });
    }

    var line = makeLine([ 250, 125, 250, 175 ]),
      line2 = makeLine([ 250, 175, 250, 250 ]),
      line3 = makeLine([ 250, 250, 300, 350]),
      line4 = makeLine([ 250, 250, 200, 350]),
      line5 = makeLine([ 250, 175, 175, 225 ]),
      line6 = makeLine([ 250, 175, 325, 225 ]);

    canvas.add(line, line2, line3, line4, line5, line6);

})();
