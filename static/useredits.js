// This script provides JavaScript functionality to yearflights.html page

var addFlight = function(result){
    //If user's flight is successfully added to db, adds row on the existing table with the new flight's data and clear the add flight form should user want to add another flight. If flight not added, pops up invalid alert message.
    if (result === "Error"){
        var err_message = "Flight not added!\n\nYou must accept and submit an airport from the suggested list, please try again.";
        alert(err_message);
    } else {
        //Create an empty <tr> element and add it to the 2nd position (under the new flight add form) of the table:
        var table = document.getElementById("report");
        var row = table.insertRow(2);
        //Insert new cells (<td> elements) at its respecitve position of the "new" <tr> element:
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);
        var cell6 = row.insertCell(5);
        var tRow = ('row-' +result.id);
        row.id = tRow;
        //Add data and classes to new cells:
        cell1.innerHTML = result.date;
        $(cell1).addClass("first_col");
        cell2.innerHTML = result.depart;
        cell3.innerHTML = result.arrive;
        cell4.innerHTML = (result.CO2e).toFixed(2);
        $(cell4).addClass("emiss results");
        $(cell4).attr("data-amt", result.CO2e);
        cell5.innerHTML = ('$' +((result.price).toFixed(2)).toString());
        $(cell5).addClass("priced results");
        $(cell5).attr("data-amt", result.price);
        $(cell6).addClass("last_col");
        //intializing cell-specific delete button that will be functional imediately to allow user to delete flight if desired
        cell6.innerHTML ='<button type="button" class="btn btn-sm btn-danger" style="visibility: hidden" id="row-entry.id" onclick="deleteFlight(\''+result.id+'\', \''+tRow+'\',\''+result.CO2e+'\')">DELETE</button>';
        //call to update table totals considering new flight addition
        addTotals();
        //updating dashboard as well accordingly
        carbonDebt = carbonDebt + result.CO2e;
        setDashboard();
}};

var deleteFlight = function(id, tRow, CO2e){
    //Asks user to confirm flight deletion then deletes flight with ajax. This function is called using an 'onclick' method directly from the html.
    if (confirm("Are you sure you want to delete this flight?")) {
        var formData = new FormData();
        formData.append("id", id);

        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", "/delete_flight", true);

        xmlhttp.onreadystatechange = function(){
            if (xmlhttp.readyState == 4){
                if (xmlhttp.responseText == "OK"){
                    var row = document.getElementById(tRow);
                    row.remove();
                    addTotals();
                    carbonDebt = carbonDebt - CO2e;
                    setDashboard();

                } else {
                    alert("Flight cannot be removed right now.");
                }
            }
        };
        xmlhttp.send(formData);
    } else {
    // Do nothing
}};

$(document).ready(function () {
    // Calculate and populate the totals for each results table
    addTotals();
   
    // Make airport city and code data available to input boxes for user-added flights, variable 'data' is assigned on the html page
    $("#arrive").autocomplete({source: data});
    $("#depart").autocomplete({source: data});
      
    // Give flight rows ability to delete flights by displaying such button on mouseover 
    $('table').on('mouseover', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'visible'});
    }).on('mouseout', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'hidden'});
    });

    //when user clicks to add new flight, submits data to server and calls addFlight function to actually add the flight to table
    $('#flightsubmit').on('click', function(e){
        e.preventDefault();
        var data = $(this).closest('div').find("input").serialize();
        $.get('/add_flight', data, addFlight);
        //clears submitted text from airports input boxes so blank for new additions
        //date not cleared out intentionally because next segment likely to be close to same date
        $(this).closest('div').find('input[type="text"]').val("");
    });

});




