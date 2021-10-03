var liked = [];

var dislike_url = window.location.origin + "/dislike_project";
var like_url = window.location.origin + "/like_project";

function like_or_dislike(isLike, id){
    var xhr = new XMLHttpRequest();
    if(isLike){
        xhr.open("POST", like_url);
    }else{
        xhr.open("POST", dislike_url);
    }
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
        console.log(xhr.status);
        console.log(xhr.responseText);
    }};

    data = `{"id":` + id + `}`
    xhr.send(data);
}