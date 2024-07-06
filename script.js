$(document).ready(function(){
    // Function to handle form submission and image upload
    function detectTumor() {
        // Code for handling form submission and image upload
        // After processing, set the result message
        var resultMessage = "Tumor detected"; // Replace this with the actual result message
        document.getElementById("result-message").innerText = resultMessage;
    }

    // Submit event handler for the image form
    $("#image-form").submit(function(event){
        event.preventDefault(); // Prevent form submission
        
        // Client-side validation
        var name = $("#name").val();
        var age = $("#age").val();
        var gender = $("#gender").val();
        var image = $("#image").val();
        
        if (name === '' || age === '' || gender === '' || image === '') {
            $("#result-message").text("Please fill in all fields and upload an image.");
            return;
        }

        // Display processing message
        $("#result-message").text("Processing...");

        var formData = new FormData($("#image-form")[0]);
        
        // AJAX request to predict endpoint
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            xhr: function() {
                // Create an XMLHttpRequest to track upload progress
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total * 100;
                        $("#upload-progress").css('width', percentComplete + '%');
                    }
                }, false);
                return xhr;
            },
            success: function(response) {
                // Show result message with advanced animation
                $("#result-message")
                    .css({ opacity: 0, top: -20 })
                    .text(response)
                    .animate({ opacity: 1, top: 0 }, 500);

                // Generate PDF using jsPDF
                var pdf = new jsPDF();
                pdf.text(20, 20, 'Result Message: ' + response);
                pdf.text(20, 40, 'User Details:');
                pdf.text(30, 50, 'Name: ' + name);
                pdf.text(30, 60, 'Age: ' + age);
                pdf.text(30, 70, 'Gender: ' + gender);
                // Add more content to the PDF as needed
                // Save the PDF
                pdf.save('report.pdf');
                
                // Add download link for the PDF
                var downloadLink = '<a href="' + pdf.output('bloburl') + '" download="report.pdf">Download PDF</a>';
                $("#download-pdf").html(downloadLink);
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
                $("#result-message").text("Error occurred. Please try again.");
            }
        });
    });
});
