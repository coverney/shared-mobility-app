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
source('utils.R')

vars <- c("Percent Available"="mean_perc_avail", "Average # Available" = "mean_avg_count", "Probability Available"="mean_prob_avail", 
          "Trips"="mean_trips", "Adjusted Trips"="mean_adj_trips")

# Define UI for application that draws a histogram
ui <- fluidPage(
    

    # Application title
    titlePanel("Shared-Mobility Data and Demand"),

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
            
            tags$hr(),
            tags$p("OR upload a previously processed file"),
            
            fileInput("demand", "Choose Processed CSV File", 
                      accept = c("text/csv",
                                 "text/comma-separated-values,text/plain",
                                 ".csv")),
            
            tags$hr(),

            actionButton("go", "Go!"),
            
            # Horizontal line ----
            tags$hr(),
            
            actionButton("var_desc", "Variable Descriptions")
            
            
        ),

        # Show a plot of the generated distribution
        mainPanel(
            textOutput(outputId = "status"), 
            uiOutput("download"),
            fluidRow(
                column(3, uiOutput("start_date_selection")),
                column(3, uiOutput("end_date_selection"))
            ),
            fluidRow(
                column(6, conditionalPanel(
                    "input.go > 0",
                    selectInput("var1", "Variable to Plot", vars)
                ),
                       leafletOutput("var1_plot")),
                #column(6, uiOutput("var2_selection"))
            ),
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    

    # ------------------ App virtualenv setup (Do not edit) ------------------- #
    source('.Rprofile')
    virtualenv_dir = Sys.getenv('VIRTUALENV_NAME')
    python_path = Sys.getenv('PYTHON_PATH')
    
    # Create virtual env and install dependencies
    reticulate::virtualenv_create(envname = virtualenv_dir, python = python_path)
    reticulate::virtualenv_install(virtualenv_dir, packages = PYTHON_DEPENDENCIES, ignore_installed=TRUE)
    reticulate::use_virtualenv(virtualenv_dir, required = T)
    
    # Import python functions to R
    reticulate::source_python('DataProcessor.py')
    print("HERE")
    
    processData <- eventReactive(input$go,{
        if(is.null(input$demand)){
            req(input$events)
            req(input$locations)
            showModal(modalDialog("Data is processing. A pop-up will appear when the process is complete.", footer = modalButton("Close")))
            df_events = read.csv(input$events$datapath)
            df_locations = read.csv(input$locations$datapath)
            start_date <- min(as.Date(df_events$event_time))
            end_date <- max(as.Date(df_events$event_time))
            df_demand <- process_reticulate(df_events, df_locations, input$grid_size, input$prob_0/100) %>%
               filter(as.Date(date) >= as.Date(start_date) & as.Date(date) <= as.Date(end_date))
            df_demand$left_lng = as.numeric(df_demand$left_lng)
            df_demand$right_lng = as.numeric(df_demand$right_lng)
            df_demand$upper_lat = as.numeric(df_demand$upper_lat)
            df_demand$lower_lat = as.numeric(df_demand$lower_lat)
            showModal(modalDialog("Data is ready!", footer = modalButton("Close")))
            return(df_demand)
        } else{
            req(input$demand)
            df_demand = read.csv(input$demand$datapath)
        }
        
        return(df_demand)
    })
    
    varDescription <- observeEvent(input$var_desc,{
        showModal(modalDialog(title = "Variable Descriptions", 
                            HTML("Average Number Available (avail_count): average number of scooters available
                              during that day. <br>
                              Available Minutes (avail_mins): minutes at least one scooter available. <br>
                              Probability Available (prob_scooter_avail): Estimated probability a randomly 
                              arriving user will find a scooter available within the user's threshold. <br>
                              Trips (trips): Number of trips from scooters in this cell. <br>
                              Adjusted Trips (adj_trips): Estimated number of trips originating from users 
                              in this cell. <br>
                              <br>
                              Percent available can be calculated by dividing avail_mins by 24*60. <br>
                              Estimated demand can be calculated by dividing the average adjusted trips
                              by average probability available.")))
    })
    
    output$start_date_selection <- renderUI({
        df_demand = processData()
        tagList(
            dateInput("start_date", label = "Start Date", 
                        min = min(df_demand$date), max = max(df_demand$date), value = min(df_demand$date))
        )
    })
    
    output$end_date_selection <- renderUI({
        df_demand = processData()
        tagList(
            dateInput("end_date", label = "End Date", 
                      min = min(df_demand$date), max = max(df_demand$date), value = max(df_demand$date))
        )
    })
    
    output$var1_plot <- renderLeaflet({
        sqrt_vars <- c("mean_trips", "mean_adj_trips")
        sqrt_scale <- FALSE
        if (input$var1 %in% sqrt_vars){
            sqrt_scale <- TRUE
        }
        df_demand = processData()
        summary_df = summarize_data(df_demand, input$start_date, input$end_date)
        genMap(summary_df, input$var1, sqrt_scale)
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
            downloadButton('df_file', "Download Data")
        )
    })    

    
    output$status <- renderText({
        result <- processData()
        if(is.null(input$demand)){
            result <- processData()
            paste("Last processed: ",Sys.time())
        } else{
            paste("Last uploaded: ", Sys.time())
        }
        
    })
    
    
    
}

# Run the application 
shinyApp(ui = ui, server = server)
