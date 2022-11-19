var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
document.getElementsByTagName('head')[0].appendChild(script);

function display(event)
{
	let input_image = document.getElementById("input_image")
	input_image.src = URL.createObjectURL(event.target.files[0]);
	document.getElementById("input_image_container").style.display = "block";
}
