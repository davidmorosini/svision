
var start_server = false;

var epi = 0;
var no_epi = 0;
var person = 0;

function set_display_values(values){

  var check = false;
  if(values['webserver']){
    check = true;
  }
  
  var client_c = "not-connected";
  var client_color = 'red';
  
  if(values['client']){
    client_c = "connected";
    client_color = 'green';
  }
  
  var client_connected = document.getElementById('client_con');
  client_connected.innerText = client_c;
  //client_connected.innerHTML.style.color = client_color;
  document.getElementById('myonoffswitch').checked = check
  document.getElementById('noepi_count').innerText = values['no_epi'];
  document.getElementById('epi_count').innerText = values['epi'];
  document.getElementById('person_count').innerText = values['person'];
}

function att_status(){
  $.ajax({
    type:'get',
    url:'att',
    cache:false,
    async:'asynchronous',
    dataType:'json',
    success: function(data) {
      set_display_values(data);
    },
    error: function(request, status, error) {
      set_display_values({
        "webserver":False,
        "client":False,
        "person":0,
        "epi":0,
        "no_epi":0
      })
    }
  });
}

function start_webpage(){
  att_status();
  var variavel = setInterval(function() {
    att_status();
  }, 4000);
}

function toggle_service(){
  start_server = !start_server;

    console.log(start_server)
    
    var req = '/service';
    
    $.ajax({
        type:'get',
        url:req,
        cache:false,
        async:'asynchronous',
        dataType:'json',
        success: function(data) {
          set_display_values(data);
        },
        error: function(request, status, error) {
          console.log("Error: " + error)
        }
     });
}