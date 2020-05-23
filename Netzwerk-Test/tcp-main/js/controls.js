function getLogData(){
	$.get("/static/log.txt", function(data){
		$("#logWindow").html(data);
	});
}

$(document).ready(function(){

	//setInterval(getLogData(),2000);
	setInterval(function(){$("#logWindow").load("/static/Pack.log");},2000);

});
