var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
document.getElementsByTagName('head')[0].appendChild(script);



      function display(event)
	{
		let input_image = document.getElementById("input_image")
		input_image.src = URL.createObjectURL(event.target.files[0]);
		document.getElementById("input_image_container").style.display = "block";
	}
    
//Predict emotion and display output
async function predict_emotion()
	{
        // header("Access-Control-Allow-Origin: *");
        var getJSON = function(url, callback) {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, true);
            // xhr.setHeader("X-PINGOTHER", "pingpong");
            xhr.setRequestHeader('Access-Control-Allow-Headers', 'https://firebasestorage.googleapis.com');
            xhr.setRequestHeader('Access-Control-Allow-Origin', 'https://firebasestorage.googleapis.com');
            xhr.responseType = 'json';
            xhr.onload = function() {
              var status = xhr.status;
              if (status === 200) {
                callback(null, xhr.response);
              } else {
                callback(status, xhr.response);
              }
            };
            xhr.send();
        };
        
        var model;

        getJSON('https://firebasestorage.googleapis.com/v0/b/ibmclassifierjs.appspot.com/o/model.json?alt=media&token=82eed334-d399-4949-8224-67650de43758', 
            function(err, data) {
                if (err !== null) {
                    alert('Something went wrong: ' + err);
                } else {
                    model = tf.loadLayersModel(data)
                }
        });

        // const model = await tf.loadLayersModel('https://firebasestorage.googleapis.com/v0/b/ibmclassifierjs.appspot.com/o/model.json?alt=media&token=82eed334-d399-4949-8224-67650de43758');	
        
		let input = document.getElementById("input_image");

		let step1 = tf.browser.fromPixels(input).resizeNearestNeighbor([64,64]).expandDims(0);
		pred = model.predict(step1)
		pred.print()
		console.log("End of predict function")
		
		arr_types = ["Left Bundle Branch Block", "Normal", "Premature Atrial Contraction", "Premature Ventricular Contractions", "Right Bundle Branch Block", "Ventricular Fibrillation"]

		pred.data()
		    .then((data) => {console.log(data)
		    	max_val = -1
		    	max_val_index = -1
				for(let i=0;i<data.length;i++)
				{
					if(data[i] > max_val)
					{
						max_val = data[i]
						max_val_index = i
					}
				}
				ARRHYTHMIA_CLASSIFICATION = arr_types[max_val_index]
				document.getElementById("output_text").innerHTML = "<p>Emotions and corresponding scaled up probability</p><p>Emotion detected: " + ARRHYTHMIA_CLASSIFICATION
		})	

	}