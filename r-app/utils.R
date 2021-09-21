library(tidyverse)
library(sf)
library(leaflet)
library(mapview)
library(pracma)

########################## SUMMARIZE DATA ##########################

sd_wzeros = function(v, num_days){
  # Calculates standard deviation of v where there are num_days-length(v) extra zeros
  mean_v = sum(v, na.rm=TRUE)/num_days
  first_sum = sum((v-mean_v)^2)
  second_sum = (num_days-length(v))*(mean_v)^2
  return(sqrt((first_sum+second_sum)/num_days))
}

cov_wzeros = function(x, y, num_days){
  # Calculates covariance of mean x and mean x where there are num_days-length(x) extra zeros
  if (length(x) <= 3){
    return(NA)
  }
  mean_x = sum(x, na.rm=TRUE)/num_days
  mean_y = sum(y, na.rm = TRUE)/num_days
  cov_xy = sum((x-mean_x)*(y-mean_y))/(num_days*(num_days-1))
  return(cov_xy)
}

summarize_data = function(df, min_day, max_day, alpha=0.1) {
  # Create summarized version of data with estimated demand (plus CI length w/ alpha given)
  # Summarizes variables over days between min day and max day
  
  df$date = as.Date(df$date) 
  num_days = as.numeric(as.Date(max_day) - as.Date(min_day) + 1)
  z_alpha = qnorm(1-alpha/2)
  summary_df = df %>% 
    filter(df$date <= as.Date(max_day) & df$date >= as.Date(min_day)) %>%
    group_by(left_lng, right_lng, lower_lat, upper_lat) %>%
    summarize("mean_perc_avail" = sum(avail_mins, na.rm=TRUE)/(24*60*num_days),
              "sd_perc_avail" = sd_wzeros(avail_mins/(24*60), num_days), 
              "mean_avg_count" = sum(avail_count, na.rm=TRUE)/num_days,
              "sd_avg_count" = sd_wzeros(avail_count, num_days), 
              "mean_prob_avail" = sum(prob_scooter_avail, na.rm=TRUE)/num_days, 
              "sd_prob_avail" = sd_wzeros(prob_scooter_avail, num_days),
              "mean_trips" = sum(trips, na.rm=TRUE)/num_days, 
              "sd_trips" = sd_wzeros(trips, num_days),
              "mean_adj_trips" = sum(adj_trips, na.rm=TRUE)/num_days, 
              "sd_adj_trips" = sd_wzeros(adj_trips, num_days),
              "est_demand" = sum(adj_trips, na.rm=TRUE)/sum(prob_scooter_avail, na.rm=TRUE),
              "cov_trips_avail" = cov_wzeros(adj_trips, prob_scooter_avail, num_days)
    )
    summary_df = summary_df %>% 
      mutate("cor_trips_avail" = num_days*cov_trips_avail/(sd_adj_trips*sd_prob_avail),
                "enough_avail" = ifelse(mean_prob_avail-z_alpha*sd_prob_avail/2 <0, FALSE, TRUE),
                "ci_len" = abs(est_demand)*z_alpha*sqrt((sd_adj_trips)^2/(num_days*mean_adj_trips^2)+
                                                          (sd_prob_avail)^2/(num_days*mean_prob_avail)^2-
                                                          2*cov_trips_avail/(mean_adj_trips*mean_prob_avail))
                  
      ) %>%
      select(-c(cov_trips_avail))
    
   
  # NA if not enough data or numeric error
  summary_df[summary_df == Inf] = NA
  summary_df = data.frame(sapply(summary_df, function(x) ifelse(is.nan(x), NA, x)))
  summary_df$ci_len[summary_df$enough_avail == FALSE] = NA
  summary_df$est_demand[summary_df$enough_avail == FALSE] = NA
  
  return(summary_df)
}


########################## PLOT DATA ##########################

getRect = function(left_lng, right_lng, lower_lat, upper_lat) {
  # Creates rectangle polygon from lat and lng values
  nw.x = left_lng; nw.y = upper_lat;
  ne.x = right_lng; ne.y = upper_lat;
  se.x = right_lng; se.y = lower_lat;
  sw.x = left_lng; sw.y = lower_lat;
  
  # use vectors to arrange them in a matrix
  cx = c(nw.x, ne.x, se.x, sw.x, nw.x);
  cy = c(nw.y, ne.y, se.y, sw.y, nw.y);
  coord = matrix(c(cx, cy), ncol=2, nrow = 5 )
  
  # create the polygon and return
  poly = st_polygon(list(coord))
  return(poly)
}

addGeo = function(summary_df) {
   # Adds geometry column to summary_df based on lat/lng values
  summary_df %>%
    rowwise() %>%
    mutate(geometry = list(getRect(left_lng, right_lng, lower_lat, upper_lat))) %>%
    st_as_sf(sf_column_name = "geometry")
}


popupHTML = function(summary_df){
  # Creates tooltips with means and standard deviations of variables plus demand CI
  sprintf( 
     "<style>
       th, td {
         padding-right: 5px;
       }
     </style>
     <strong>%s</strong><br>
     <table>
       <tr>
         <td>Mean Percent of Day Available</td>
         <td>%s</td>
       </tr>
       <tr>
         <td>Mean Average # Available</td>
         <td>%s</td>
       </tr>
       <tr>
         <td>Probability Available</td>
         <td>%s</td>
       </tr>
       <tr>
         <td>Mean Trips</td>
         <td>%s</td>
       </tr>
       <tr>
         <td>Mean Adjusted Trips</td>
         <td>%s</td>
       </tr>
       <tr>
         <td>Estimated Demand</td>
         <td>%s</td>
       </tr>
     </table>
     ",
     paste("Lower Left Point: (", summary_df$left_lng, ",", summary_df$lower_lat,") Upper Right Point: (",
           summary_df$right_lng, ",", summary_df$upper_lat, ")"),
     paste(round(summary_df$mean_perc_avail, 3), " (sd: ", round(summary_df$sd_perc_avail,3), ")"),
     paste(round(summary_df$mean_avg_count, 3), " (sd: ", round(summary_df$sd_avg_count,3), ")"),
     paste(round(summary_df$mean_prob_avail, 3), " (sd: ", round(summary_df$sd_prob_avail,3), ")"),
     paste(round(summary_df$mean_trips, 3), " (sd: ", round(summary_df$sd_trips,3), ")"),
     paste(round(summary_df$mean_adj_trips,3), " (sd: ", round(summary_df$sd_adj_trips,3), ")"),
     paste(round(summary_df$est_demand,3), " (CI: (", round(summary_df$est_demand-summary_df$ci_len,3),",",
           round(summary_df$est_demand+summary_df$ci_len,3), ")")
   ) %>% lapply(htmltools::HTML)
} 

genMap = function(summary_df, zcol, sqrt_scale = FALSE, show_labels = FALSE){
  # Plots the summary_df with zcol as the chosen column
  
  # Create labels
  label = NULL
  labelOptions = NULL
  if(show_labels){
    label = round(summary_df[,zcol], 3)
    labelOptions = labelOptions(noHide = TRUE, textOnly = TRUE)
  }
  plt_title = str_to_title(str_replace_all(zcol, "_", " "))
  
  # Get color vector and legend
  legend_vals = round(summary_df[,zcol], 3)
  lab_format = labelFormat(suffix="", digits=2)
  if (sqrt_scale){
    legend_vals = round(sqrt(summary_df[,zcol]+0.001), 3)
    lab_format = labelFormat(suffix="", transform = function(x) x^2-0.001,digits=2)
  }
  pal = colorNumeric(palette = "plasma", domain = legend_vals)
  
  # Create geometry and popups
  summary_df = addGeo(summary_df)
  popups = popupHTML(summary_df)
  
  # Put map together
  plt = leaflet() %>% 
    addProviderTiles("CartoDB.Positron") %>%
    addPolygons(data = summary_df, 
                weight = 1,
                color = "#000000",
                opacity = 1,
                fillOpacity = 0.6,
                fillColor = ~pal(legend_vals),
                smoothFactor = 0,
                label = label,
                labelOptions = labelOptions,
                popup = popups,
                highlightOptions = highlightOptions(color = "#FFFFFF", weight = 2, bringToFront = TRUE)
    ) %>%
    addLegend(position = "bottomright", pal = pal, values = legend_vals, labFormat = lab_format, opacity = 1, title = plt_title)
}

#setwd("/Users/alice/Dropbox/test_reticulate/")
#df = read.csv("processed-data-summer.csv")
#sum_data = summarize_data(df, "2019-05-01", "2019-08-31")
#plt = genMap(sum_data, "mean_trips", TRUE)

