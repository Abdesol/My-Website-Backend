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

    data = `{"id":` + id + `}`
    xhr.send(data);

    var response = true;
    xhr.onload = function (){
        if(xhr.status != 200){
            return false;
        }
    }
    return response;
}

function likeBtnStart(button, id){
    if(liked.includes(parseInt(id))){
        button.src = window.location.origin + "/static/img/liked.png"
    }else{
        button.src = window.location.origin + "/static/img/like.png"
    }
}

function loadLocalStorage() {
    var string_liked = localStorage.getItem("liked");
    if(string_liked != null){
        liked  = JSON.parse(string_liked)
    }
}