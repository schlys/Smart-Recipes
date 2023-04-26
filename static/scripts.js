//----------------- home page functions ------------------------------//
function logout() {
    fetch("/signout", {
        method: "POST"
    }).then((response) => {
        window.location.href = response.url;
    });
}

function getSelected(remove) {
    let ingredients = [];
    checkboxes = document.getElementsByName('ingredient');

    for (const ingredient of checkboxes)
        if (ingredient.checked)
            ingredients.push(ingredient.parentNode.id);

    if (remove)
        for (const ingredient of ingredients)
            document.getElementById(ingredient).remove();

    return ingredients;
}

function remove() {
    fetch("/remove_items", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'ingredients': getSelected(true)
        })
    })
}

function search() {
    fetch("/search_items", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'ingredients': getSelected()
        })
    }).then((response) => {
        window.location.href = response.url;
    });
}


function sendToSpeech() {
    event.preventDefault();
    fetch("/speech", {
        method: "POST",
    }).then((response) => {
        return response.json(); // Parse response as JSON data
    }).then((items) => {
        addIngredients(items)
    })
}

function addIngredients(items) {
    for (const item of items) {
        const div = document.createElement('div');
        div.className = 'form-check';
        div.id = item;
        div.innerHTML = `
            <input class="form-check-input" name="ingredient" type="checkbox" value="" id="flexCheckDefault" checked="true">
            <label class="form-check-label" for="flexCheckDefault">
                ${item.charAt(0).toUpperCase() + item.slice(1)}
            </label>
        `
        document.getElementById('ingredients').appendChild(div)
    }
}

var checked = true;
function selectAll() {
    checkboxes = document.getElementsByName('ingredient');
    for (checkbox of checkboxes) checkbox.checked = !checked;
    checked = !checked;
}

function handleEnterKeyDown(event) {
    if (event.keyCode === 13) { // check if Enter key was pressed
        event.preventDefault();
        let data = {ingredients: document.getElementById("text-box").value};
        fetch("/text", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then((response) => {
            return response.json();
        }).then((items) => {
            addIngredients(items)
            document.getElementById("text-box").value = "";
        })
    }
}

function takePicture() {
    fetch("/save_pic", {
        method: "POST",
    })
}


function show_ai_output() {
    // fetch("/ai-img", {
    //     method: "POST",
    //     headers: {
    //         'Content-Type': 'image/png'
    //     }
    // }).then((response) => {
    //     return response.json(); // Parse response as JSON data
    // }).then((data) => {
    //     // console.log(data);
    //     document.getElementById("ai_img").src = 'data:image/png;base64,' + data;
    // })
    // var image = document.querySelectorAll(".image-ai-result img");
    // image[0].classList.add("active");
}

// show_ai_output()


function sendImageToAI() {
    // var imageInput = document.getElementById("imageInputAI");
    // var image = imageInput.files[0];

    // var formData = new FormData();
    // formData.append("image", image);

    // fetch("/ai-rec", {
    //     method: "POST",
    //     body: formData
    // }).then((response) => {
    //     return response.json(); // Parse response as JSON data
    // }).then((items) => {
    //     addIngredients(items)
    // }).then(() => {
    //     show_ai_output();
    // })
}


function clearAllFields() {
    var inputFields = document.querySelectorAll('input, textarea');

    for (var i = 0; i < inputFields.length; i++) {
        if (inputFields[i].type === 'file') {
            inputFields[i].value = null;
        } else {
            inputFields[i].value = "";
        }
    }
}

//----------------- results page functions ------------------------------//
function toggleLikes(like) {
    let counter = document.getElementById('counter-' + like.id);
    let liked = true;

    if (like.name == 'False') {
        like.src = "static/images/True.png";
        like.name = "True";
        counter.innerHTML = Number(counter.innerHTML) + 1;
    } else {
        like.src = "static/images/False.png";
        like.name = "False";
        counter.innerHTML = Number(counter.innerHTML) - 1;
        liked = false;
    }

    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'id': like.id,
            'count': counter.innerHTML,
            'liked': liked
        })
    })
}

