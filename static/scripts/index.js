function navigateById(documentId) {
    console.log(documentId);
    x = document.getElementById('form');
    x.setAttribute('action', '/document/' + documentId + '/');
    document.getElementById('input').click();
}