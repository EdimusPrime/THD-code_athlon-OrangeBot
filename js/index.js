$(document).ready(function() {

//TWITTER WIDET TO PULL TWEETS 

twttr.widgets.createTimeline(
  {
    sourceType: "profile",
    screenName: "TwitterDev"
  },
  document.getElementById("container")
);


// PULLS RANDOM TICKET NUMBERS,NAMES, UPDATED DATES & STATUS 
// TO POPULATE FICTIONAL ACTIVITY LOG



$.ajax({
  url: 'https://randomuser.me/api/?results=45',
  dataType: 'json',
  success: function(data) {
    // console.log(data);

    for (var i=0; i<data.results.length; i++){

    	var status = Math.floor(Math.random() * 400);
    	var ticket = data.results[i].id.value;
    	var lastName = data.results[i].name.last;
    	var updateDate = data.results[i].registered;
    	

		if (status<201){ 
			status="closed"
			// $(".status").css("color", "red")


		} else {
			status="open"
			// $(".status").css("color", "green")	
		}

		if (ticket == null){
			var ticket = Math.floor(Math.random() * 9000000000);
		}


  		$(".activity_log").prepend(
  			"<div class = 'row'>" + "<a href=#><div class='ticket col-md-3 '>" + ticket + "</div></a>"+
  			"<div class='last_name col-md-3 '>" + lastName + "</div>" +
  			"<div class='date_updated col-md-3 '>" + updateDate + "</div>" +
  			"<div class='status col-md-3 '>" + status + "</div>" + "</div>"
  			);


    }	

  }
});



});