// TODO: move javascript into file and source file into this page, either source on bottom or wrap in .ready tag
var addTotals = function(){
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
    // Want this function to, if successfully added to db, add a row on the existing table with the new flight's data and clear the add flight form should user want to add another flight
    console.log(result);
    if (result === "OK"){
        console.log("YOU ARE THE BEST");
    } else {
        alert(result);
}};

var deleteFlight = function(id, tRow){
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
    $('#flightaddform').submit(function(e){
        e.preventDefault();
        var data = $(this).serialize();
        console.log(data);

        // want it to submit to route /add_flight which will parse out the form data and make a new flight entry in the db, then run addFlight function
        $.get('/add_flight', data, addFlight);

    });

    addTotals();
    $("#arrive").autocomplete({source: data});
    $("#depart").autocomplete({source: data});
      
    $('table').on('mouseover', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'visible'});
    }).on('mouseout', 'tr', function(ev) {
        $(this).find('.btn.btn-danger').css({'visibility': 'hidden'});
    });

});
