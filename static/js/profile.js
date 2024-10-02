document.getElementById("profile-icon").onclick = function() {
    var perfilExpanded = document.getElementById("perfil-expanded");
    if (perfilExpanded.style.display === "none" || perfilExpanded.style.display === "") {
        perfilExpanded.style.display = "block";
    } else {
        perfilExpanded.style.display = "none";
    }
};