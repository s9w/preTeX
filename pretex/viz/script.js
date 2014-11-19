function body_ready(){

}

function showCoords(evt, p1){
    var ibox = document.getElementById("ibox");
    ibox.style.left = evt.pageX+5+"px";
    ibox.style.top = evt.pageY+20+"px";
    ibox.innerHTML= p1;
}

function hideBox(event){
    document.getElementById("ibox").className = "invisible";
}

function showBox(event){
    document.getElementById("ibox").className = ' ';
}
