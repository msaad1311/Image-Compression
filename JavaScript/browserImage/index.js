// async function handleImageUpload(event) {

//     const imageFile = event.target.files[0];
//     console.log(typeof (imageFile))
//     console.log(imageFile)
//     console.log('originalFile instanceof Blob', imageFile instanceof Blob); // true
//     console.log(`originalFile size ${imageFile.size / 1024 / 1024} MB`);

//     const options = {
//         maxSizeMB: 1,
//         maxWidthOrHeight: 180,
//         useWebWorker: true
//     }
//     try {
//         const compressedFile = await imageCompression(imageFile, options);
//         console.log('compressedFile instanceof Blob', compressedFile instanceof Blob); // true
//         console.log(`compressedFile size ${compressedFile.size / 1024 / 1024} MB`); // smaller than maxSizeMB
//         console.log(compressedFile)

//         await uploadToServer(compressedFile); // write your own logic
//     } catch (error) {
//         console.log(error);
//     }

// }

function starter() {

    // Grab elements, create settings, etc.
    var video = document.getElementById('video');

    // Get access to the camera!
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Not adding `{ audio: true }` since we only want video now
        navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
            //video.src = window.URL.createObjectURL(stream);
            video.srcObject = stream;

            setInterval(function(){ 
                const track = stream.getVideoTracks()[0];
                imageCapture = new ImageCapture(track);
                imageCapture.takePhoto().then(function (blob) {
                    compressor(blob)
                }).catch(function (error) {
                    console.log('takePhoto() error: ', error);
                });
                video.play();

             }, 100);
            
        });
    }

}

async function compressor(blob) {
    console.log('originalFile instanceof Blob', blob instanceof Blob); // true
    console.log(`originalFile size ${blob.size / 1024 / 1024} MB`);

    const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 640,
        useWebWorker: true,   
        initialQuality: 1 
    }
    try {
        var canvas = document.getElementById("output")
        var ctx = canvas.getContext("2d")
        var myFile = new File([blob], "name.jpg");
        console.log('see this:', myFile)
        const compressedFile = await imageCompression(blob, options);
        console.log('compressedFile instanceof Blob', compressedFile instanceof Blob); // true
        console.log(`compressedFile size ${compressedFile.size / 1024 / 1024} MB`); // smaller than maxSizeMB
        console.log(typeof (compressedFile))
        console.log(compressedFile)
        // displaying the blob on the canvas
        var reader = new FileReader();
        reader.readAsDataURL(compressedFile);
        reader.onloadend = function () {
            var base64data = reader.result;
            var img = new Image()
            img.onload = function () {
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
            }
            img.src = base64data
            // console.log(base64data)
            // compressor(base64data);     
        }
        console.log('completed')

    } catch (error) {
        console.log('here')
        console.log(error);
    }
}

starter();