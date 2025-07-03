﻿using Microsoft.Extensions.Configuration;

// Import namespaces


string filePath = Path.GetFullPath("appsettings.json");
var config = new ConfigurationBuilder()
    .AddJsonFile(filePath)
    .Build();

// Set your values in appsettings.json
string apiKey = config["PROJECT_KEY"]!;
string endpoint = config["PROJECT_ENDPOINT"]!;
string deploymentName = config["DEPLOYMENT_NAME"]!;


// Create a kernel with Azure OpenAI chat completion


// Test the chat completion service