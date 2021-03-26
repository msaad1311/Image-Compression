async function handleImageUpload(event) {

    const imageFile = event.target.files[0];
    console.log('originalFile instanceof Blob', imageFile instanceof Blob); // true
    console.log(`originalFile size ${imageFile.size / 1024 / 1024} MB`);

    const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true
    }
    try {
        const compressedFile = await imageCompression(imageFile, options);
        console.log('compressedFile instanceof Blob', compressedFile instanceof Blob); // true
        console.log(`compressedFile size ${compressedFile.size / 1024 / 1024} MB`); // smaller than maxSizeMB
        console.log(compressedFile)

        await uploadToServer(compressedFile); // write your own logic
    } catch (error) {
        console.log(error);
    }

}

// Grab elements, create settings, etc.
var video = document.getElementById('video');

// Get access to the camera!
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    // Not adding `{ audio: true }` since we only want video now
    navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
        //video.src = window.URL.createObjectURL(stream);
        video.srcObject = stream;
        const track = stream.getVideoTracks()[0];
        imageCapture = new ImageCapture(track);
        imageCapture.takePhoto().then(function (blob) {
            console.log(blob)
            compressor(blob);        
        }).catch(function (error) {
            console.log('takePhoto() error: ', error);
        });
        video.play();
    });
}

async function compressor(blob) {
    console.log('originalFile instanceof Blob', blob instanceof Blob); // true
    console.log(`originalFile size ${blob.size / 1024 / 1024} MB`);

    const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true
    }
    try {
        var canvas = document.getElementById("output")
        var ctx = canvas.getContext("2d")
        const compressedFile = await imageCompression(blob, options);
        console.log('compressedFile instanceof Blob', compressedFile instanceof Blob); // true
        console.log(`compressedFile size ${compressedFile.size / 1024 / 1024} MB`); // smaller than maxSizeMB
        console.log(typeof (compressedFile))
        console.log(compressedFile)
        // displaying the blob on the canvas
        var img = document.createElement("img")
        var reader = new FileReader();
        reader.readAsDataURL(compressedFile); 
        reader.onloadend = function() {
            var base64data = reader.result;   
            img.src = URL.createObjectURL(base64data)             
        }
        ctx.drawImage(img,0,0)
        console.log('completed')

    } catch (error) {
        console.log(error);
    }
}