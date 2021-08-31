#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#
# Define any Python packages needed for the app here:
PYTHON_DEPENDENCIES = c('pip', 'numpy', 'pandas', 'scipy', 'iso8601',
                        'datetime', 'statsmodels')
options(shiny.maxRequestSize=100*1024^2)

library(shiny)
library(tidyverse)

# Define UI for application that draws a histogram
ui <- fluidPage(
    

    # Application title
    titlePanel("Processing Data"),

    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            fileInput("events", "Choose Events CSV File",
                      accept = c("text/csv",
                                 "text/comma-separated-values,text/plain",
                                 ".csv")),
            
            fileInput("locations", "Choose Locations CSV File",
                      accept = c("text/csv",
                                 "text/comma-separated-values,text/plain",
                                 ".csv")),
            
            sliderInput("grid_size", "Dimensions of one grid cell (in meters)", 0, 1000, 400, 50),
            
            sliderInput("prob_0", "Probability (%) a user will not consider a scooter more than one
                        grid away", 0, 100, 100, 5),

            actionButton("go", "Process"),
            
            # Horizontal line ----
            tags$hr()
            
            
        ),

        # Show a plot of the generated distribution
        mainPanel(
            textOutput(outputId = "status"), 
            uiOutput("download")
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    

    # ------------------ App virtualenv setup (Do not edit) ------------------- #
    
    virtualenv_dir = Sys.getenv('VIRTUALENV_NAME')
    python_path = Sys.getenv('PYTHON_PATH')
    
    # Create virtual env and install dependencies
    reticulate::virtualenv_create(envname = virtualenv_dir, python = python_path)
    reticulate::virtualenv_install(virtualenv_dir, packages = PYTHON_DEPENDENCIES, ignore_installed=TRUE)
    reticulate::use_virtualenv(virtualenv_dir, required = T)
    
    # Import python functions to R
    reticulate::source_python('DataProcessor.py')
    
    processData <- eventReactive(input$go,{
        req(input$events)
        req(input$locations)
        showModal(modalDialog("Data is processing. A pop-up will appear when the process is complete.", footer = modalButton("Close")))
        df_events = read.csv(input$events$datapath)
        df_locations = read.csv(input$locations$datapath)
        df_demand = process_reticulate(df_events, df_locations, input$grid_size, input$prob_0)
        df_demand$left_lng = as.numeric(df_demand$left_lng)
        df_demand$right_lng = as.numeric(df_demand$right_lng)
        df_demand$upper_lat = as.numeric(df_demand$upper_lat)
        df_demand$lower_lat = as.numeric(df_demand$lower_lat)
        showModal(modalDialog("Data is ready!", footer = modalButton("Close")))
        return(df_demand)
    })
    
    
    output$download <- renderUI({
        df_demand = processData()
        output$df_file = downloadHandler(
            filename = function() {
                paste("processed-data-", Sys.Date(), ".csv", sep="")
            },
            content = function(file) {
                write.csv(df_demand, file, row.names = FALSE)
            }
        )
        tagList(
            downloadButton('df_file', "Download Processed Data")
        )
    })    

    
    output$status <- renderText({
        result <- processData()
        paste("Last processed: ",Sys.time())
    })
    
    
    
}

# Run the application 
shinyApp(ui = ui, server = server)
