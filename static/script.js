// This script provides JavaScript functionality to yearflights.html page

var addTotals = function(){
    // Calculates and recalculates with user-edits the total carbon debt in metric tons and dollars
    var cTotal = document.getElementById("cTotal");
    var mcTotal = document.getElementById("mTotal");
    var tdEmiss = document.getElementsByClassName("emiss");
    var tdPriced = document.getElementsByClassName("priced");
    var cSum = 0 ; mSum = 0;

    for (var i = 0; i < tdEmiss.length; i++) {
        cSum += parseFloat(tdEmiss[i].innerText);
        var unpriced = tdPriced[i].innerText;
        unpriced = parseFloat(unpriced.replace(/\$/,""));
        mSum += unpriced;
        }

    cSum = cSum.toFixed(2);
    mSum = mSum.toFixed(2);
    mSum = mSum.toString();
    cTotal.innerText = cSum;
    mTotal.innerText = ("$" + mSum);
};

var addFlight = function(result){
    //If user's flight is successfully added to db, adds row on the existing table with the new flight's data and clear the add flight form should user want to add another flight. If flight not added, pops up invalid alert message.
    if (result === "OK"){
        console.log("YOU ARE THE BEST");
        // Add row to table
    } else {
        alert(result);
}};

var deleteFlight = function(id, tRow){
    // Asks user to confirm flight deletion then deletes flight with ajax. This function is called using an 'onclick' method directly from the html.
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

                } else {
                    // TODO update this to be more useful
                    console.log("Flight cannot be removed");
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

    // Add only-valid flights to db on user's request and add to table
    $('#flightaddform').submit(function(e){
        e.preventDefault();
        var data = $(this).serialize();
        $.get('/add_flight', data, addFlight);
    });

});