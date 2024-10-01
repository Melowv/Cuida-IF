document.getElementById('foto_perfil').addEventListener('change', function(event) {
    const file = event.target.files[0]; // Obtém o arquivo selecionado
    if (file) {
        const reader = new FileReader(); // Cria um novo FileReader
        reader.onload = function(e) {
            const img = document.getElementById('preview'); // Seleciona a imagem de pré-visualização
            img.src = e.target.result; // Define o src da imagem para o resultado do FileReader
            img.style.display = 'block'; // Torna a imagem visível (caso não esteja)
        };
        reader.readAsDataURL(file); // Lê o arquivo como URL de dados
    }
});

document.getElementById("profile-icon").onclick = function() {
    var perfilExpanded = document.getElementById("perfil-expanded");
    if (perfilExpanded.style.display === "none" || perfilExpanded.style.display === "") {
        perfilExpanded.style.display = "block";
    } else {
        perfilExpanded.style.display = "none";
    }
};
