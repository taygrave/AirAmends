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
    if (result === "Error"){
        var err_message = "Flight not added!\n\nYou must accept and submit an airport from the suggested list, please try again.";
        alert(err_message);
    } else {
        // Create an empty <tr> element and add it to the 1st position of the table:
        var table = document.getElementById("report");
        var row = table.insertRow(2);
        // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);
        var cell6 = row.insertCell(5);
        var tRow = ('row-' +result.id);
        row.id = tRow;
        // Add data to new cells:
        cell1.innerHTML = result.date;
        cell2.innerHTML = result.depart;
        cell3.innerHTML = result.arrive;
        cell4.innerHTML = (result.CO2e).toFixed(2);
        cell5.innerHTML = ('$' +((result.price).toFixed(2)).toString());
        cell6.innerHTML ='<button type="button" class="btn btn-danger" style="visibility: hidden" id="row-entry.id" onclick="deleteFlight(\''+result.id+'\', \''+tRow+'\')">DELETE</button>';
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
    console.log(data);
    $("#arrive").autocomplete({source: data});
    $("#depart").autocomplete({source: data});
      
    // Give flight rows ability to delete flights by displaying such button on mouseover 
    $('table').on('mouseover', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'visible'});
    }).on('mouseout', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'hidden'});
    });

    $('#flightsubmit').on('click', function(e){
    console.log("HEREEEEE");
    e.preventDefault();
    var data = $(this).closest('div').find("input").serialize();
    console.log(data);
    $.get('/add_flight', data, addFlight);
    $(this).closest('div').find('input[type="text"]').val("");
    });

});




