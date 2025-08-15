"""
Map Visualizer for Project Synapse
Provides live driver tracking and rerouting on Bangalore road maps
"""

import streamlit as st
import folium
from streamlit_folium import folium_static
import random
from typing import Dict, List, Tuple, Optional
import time

class BangaloreMapVisualizer:
    """Map visualizer for Bangalore with driver tracking and rerouting"""
    
    def __init__(self):
        # Bangalore center coordinates
        self.bangalore_center = [12.9716, 77.5946]
        
        # Predefined Bangalore locations for demo
        self.bangalore_locations = {
            "Koramangala": [12.9349, 77.6055],
            "Indiranagar": [12.9789, 77.6417],
            "Whitefield": [12.9692, 77.7499],
            "Electronic City": [12.8458, 77.6655],
            "Marathahalli": [12.9498, 77.6964],
            "HSR Layout": [12.9141, 77.6417],
            "JP Nagar": [12.9067, 77.5851],
            "Bannerghatta Road": [12.8876, 77.5970],
            "Sarjapur Road": [12.9141, 77.6417],
            "Bellandur": [12.9349, 77.6749]
        }
        
        # Predefined routes for demo
        self.demo_routes = {
            "current_route": [
                [12.9716, 77.5946],  # MG Road
                [12.9789, 77.6417],  # Indiranagar
                [12.9349, 77.6055],  # Koramangala
                [12.9141, 77.6417],  # HSR Layout
                [12.9067, 77.5851]   # JP Nagar
            ],
            "optimal_route": [
                [12.9716, 77.5946],  # MG Road
                [12.9498, 77.6964],  # Marathahalli (avoiding traffic)
                [12.9349, 77.6055],  # Koramangala
                [12.9141, 77.6417],  # HSR Layout
                [12.9067, 77.5851]   # JP Nagar
            ],
            "emergency_route": [
                [12.9716, 77.5946],  # MG Road
                [12.9692, 77.7499],  # Whitefield (backup route)
                [12.9349, 77.6055],  # Koramangala
                [12.9141, 77.6417],  # HSR Layout
                [12.9067, 77.5851]   # JP Nagar
            ]
        }
    
    def create_bangalore_map(self, driver_location: Optional[List[float]] = None, 
                           route_type: str = "current_route") -> folium.Map:
        """
        Create a Folium map centered on Bangalore with driver tracking
        
        Args:
            driver_location: Current driver coordinates [lat, lng]
            route_type: Type of route to display ("current_route", "optimal_route", "emergency_route")
            
        Returns:
            Folium map object
        """
        # Create map centered on Bangalore with better styling
        m = folium.Map(
            location=self.bangalore_center,
            zoom_start=11,
            tiles='CartoDB positron',  # Cleaner tile style
            control_scale=True
        )
        
        # Add a title to the map
        title_html = '''
        <h3 align="center" style="font-size:16px"><b>🚗 Bangalore Delivery Route</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add Bangalore landmarks with better styling
        for name, coords in self.bangalore_locations.items():
            folium.Marker(
                coords,
                popup=f"<b>📍 {name}</b><br>Delivery Point<br>Coordinates: [{coords[0]:.4f}, {coords[1]:.4f}]",
                tooltip=f"📍 {name}",
                icon=folium.Icon(color='blue', icon='info-sign', prefix='fa')
            ).add_to(m)
        
        # Add driver location if provided
        if driver_location:
            folium.Marker(
                driver_location,
                popup=f"<b>🚗 Driver Location</b><br>Real-time tracking<br>Coordinates: [{driver_location[0]:.4f}, {driver_location[1]:.4f}]",
                tooltip="🚗 Driver Location",
                icon=folium.Icon(color='red', icon='car', prefix='fa')
            ).add_to(m)
        
        # Add route with better styling
        if route_type in self.demo_routes:
            route_coords = self.demo_routes[route_type]
            
            # Different colors for different route types
            color_map = {
                "current_route": "red",
                "optimal_route": "green", 
                "emergency_route": "orange"
            }
            
            # Create route line
            folium.PolyLine(
                route_coords,
                color=color_map.get(route_type, "blue"),
                weight=6,
                opacity=0.8,
                popup=f"<b>Route: {route_type.replace('_', ' ').title()}</b><br>Click for details"
            ).add_to(m)
            
            # Add route markers with better styling
            for i, coord in enumerate(route_coords):
                folium.CircleMarker(
                    coord,
                    radius=8,
                    color=color_map.get(route_type, "blue"),
                    fill=True,
                    fillColor=color_map.get(route_type, "blue"),
                    fillOpacity=0.7,
                    popup=f"<b>Stop {i+1}</b><br>Coordinates: [{coord[0]:.4f}, {coord[1]:.4f}]",
                    tooltip=f"Stop {i+1}"
                ).add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 90px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Map Legend</b></p>
        <p><i class="fa fa-car" style="color:red"></i> Driver Location</p>
        <p><i class="fa fa-info-sign" style="color:blue"></i> Delivery Points</p>
        <p><span style="color:red">●</span> Current Route</p>
        <p><span style="color:green">●</span> Optimal Route</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def create_traffic_analysis_map(self) -> folium.Map:
        """
        Create a traffic analysis map showing accident route vs alternative route
        
        Returns:
            Folium map object with traffic analysis
        """
        # Create map centered on Bangalore
        m = folium.Map(
            location=self.bangalore_center,
            zoom_start=11,
            tiles='CartoDB positron',
            control_scale=True
        )
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:16px"><b>🚦 Traffic Analysis - Highway Accident</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add Bangalore landmarks
        for name, coords in self.bangalore_locations.items():
            folium.Marker(
                coords,
                popup=f"<b>📍 {name}</b><br>Delivery Point<br>Coordinates: [{coords[0]:.4f}, {coords[1]:.4f}]",
                tooltip=f"📍 {name}",
                icon=folium.Icon(color='blue', icon='info-sign', prefix='fa')
            ).add_to(m)
        
        # Accident route (red) - Highway 1 with accident
        accident_route = [
            [12.9716, 77.5946],  # MG Road
            [12.9789, 77.6417],  # Indiranagar (accident location)
            [12.9349, 77.6055],  # Koramangala
            [12.9141, 77.6417],  # HSR Layout
            [12.9067, 77.5851]   # JP Nagar
        ]
        
        # Alternative route (green) - via Marathahalli-Bellandur
        alternative_route = [
            [12.9716, 77.5946],  # MG Road
            [12.9498, 77.6964],  # Marathahalli (avoiding accident)
            [12.9349, 77.6749],  # Bellandur
            [12.9141, 77.6417],  # HSR Layout
            [12.9067, 77.5851]   # JP Nagar
        ]
        
        # Add accident route (red)
        folium.PolyLine(
            accident_route,
            color='red',
            weight=8,
            opacity=0.8,
            popup="<b>🚨 Accident Route (High Traffic)</b><br>Major accident on Highway 1<br>45+ min delay expected"
        ).add_to(m)
        
        # Add alternative route (green)
        folium.PolyLine(
            alternative_route,
            color='green',
            weight=8,
            opacity=0.8,
            popup="<b>🟢 Alternative Route (Low Traffic)</b><br>Via Marathahalli-Bellandur<br>15 min delay expected"
        ).add_to(m)
        
        # Add accident location marker (red with warning icon)
        folium.Marker(
            [12.9789, 77.6417],  # Indiranagar - accident location
            popup="<b>🚨 MAJOR ACCIDENT</b><br>Highway 1 - Indiranagar<br>Police and ambulance on scene<br>Traffic blocked in both directions",
            tooltip="🚨 ACCIDENT LOCATION",
            icon=folium.Icon(color='red', icon='warning', prefix='fa')
        ).add_to(m)
        
        # Add alternative route highlight marker (green)
        folium.Marker(
            [12.9498, 77.6964],  # Marathahalli - alternative path
            popup="<b>🟢 ALTERNATIVE PATH</b><br>Marathahalli Route<br>Low traffic, recommended<br>15 min delay only",
            tooltip="🟢 ALTERNATIVE PATH",
            icon=folium.Icon(color='green', icon='check-circle', prefix='fa')
        ).add_to(m)
        
        # Add route markers
        for i, coord in enumerate(accident_route):
            if i == 1:  # Accident location
                folium.CircleMarker(
                    coord,
                    radius=12,
                    color='red',
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.8,
                    popup=f"<b>🚨 Stop {i+1} - ACCIDENT</b><br>Coordinates: [{coord[0]:.4f}, {coord[1]:.4f}]"
                ).add_to(m)
            else:
                folium.CircleMarker(
                    coord,
                    radius=8,
                    color='red',
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.6,
                    popup=f"<b>Stop {i+1}</b><br>Coordinates: [{coord[0]:.4f}, {coord[1]:.4f}]"
                ).add_to(m)
        
        for i, coord in enumerate(alternative_route):
            if i == 1:  # Alternative path
                folium.CircleMarker(
                    coord,
                    radius=12,
                    color='green',
                    fill=True,
                    fillColor='green',
                    fillOpacity=0.8,
                    popup=f"<b>🟢 Stop {i+1} - ALTERNATIVE</b><br>Coordinates: [{coord[0]:.4f}, {coord[1]:.4f}]"
                ).add_to(m)
            else:
                folium.CircleMarker(
                    coord,
                    radius=8,
                    color='green',
                    fill=True,
                    fillColor='green',
                    fillOpacity=0.6,
                    popup=f"<b>Stop {i+1}</b><br>Coordinates: [{coord[0]:.4f}, {coord[1]:.4f}]"
                ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 250px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Traffic Analysis Legend</b></p>
        <p><span style="color:red">●</span> Accident Route (High Traffic)</p>
        <p><span style="color:green">●</span> Alternative Route (Low Traffic)</p>
        <p><i class="fa fa-warning" style="color:red"></i> Accident Location</p>
        <p><i class="fa fa-check-circle" style="color:green"></i> Alternative Path</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def get_driver_location(self) -> List[float]:
        """Get simulated driver location in Bangalore"""
        # Simulate driver moving through Bangalore
        locations = list(self.bangalore_locations.values())
        return random.choice(locations)
    
    def calculate_optimal_route(self, current_location: List[float], 
                              destination: List[float]) -> List[List[float]]:
        """
        Calculate optimal route avoiding traffic
        
        Args:
            current_location: Current driver location
            destination: Destination coordinates
            
        Returns:
            List of route coordinates
        """
        # Simulate route calculation with traffic avoidance
        # In a real implementation, this would use Google Maps API or similar
        
        # For demo, return a route that avoids known traffic areas
        return [
            current_location,
            [12.9498, 77.6964],  # Marathahalli (avoiding traffic)
            [12.9349, 77.6055],  # Koramangala
            destination
        ]
    
    def display_live_driver_map(self, route_type: str = "current_route"):
        """Display live driver map in Streamlit"""
        try:
            st.subheader("🚗 Live Driver Tracking - Bangalore")
            
            # Get current driver location
            driver_location = self.get_driver_location()
            
            # Create map
            map_obj = self.create_bangalore_map(driver_location, route_type)
            
            # Display map with better error handling
            try:
                folium_static(map_obj, width=700, height=500)
                st.success("🗺️ Map loaded successfully!")
            except Exception as map_error:
                st.error(f"❌ Error displaying map: {map_error}")
                st.info("Trying alternative map display...")
                # Fallback: show map as HTML
                try:
                    st.components.v1.html(map_obj._repr_html_(), height=500)
                    st.success("✅ Map displayed using HTML fallback!")
                except Exception as html_error:
                    st.error(f"❌ HTML fallback also failed: {html_error}")
            
            # Display driver info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Driver Status", "🟢 Active")
            
            with col2:
                st.metric("Current Speed", f"{random.randint(20, 60)} km/h")
            
            with col3:
                st.metric("ETA", f"{random.randint(15, 45)} min")
            
            # Route information
            route_info = {
                "current_route": "Current route with traffic delays",
                "optimal_route": "Optimized route avoiding traffic",
                "emergency_route": "Emergency backup route"
            }
            
            st.info(f"📍 **Route Type**: {route_info.get(route_type, 'Unknown route')}")
            
            # Show route coordinates
            if route_type in self.demo_routes:
                st.markdown("---")
                st.subheader("📍 **Route Coordinates & Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Route Waypoints:**")
                    for i, coord in enumerate(self.demo_routes[route_type]):
                        st.write(f"  **{i+1}.** [{coord[0]:.4f}, {coord[1]:.4f}]")
                
                with col2:
                    st.write("**Driver Location:**")
                    st.write(f"  **Current:** [{driver_location[0]:.4f}, {driver_location[1]:.4f}]")
                    st.write(f"  **Status:** Active & Tracking")
                    st.write(f"  **Route Type:** {route_type.replace('_', ' ').title()}")
                
                # Add a note about the coordinates
                st.info("🗺️ **Map Info:** This shows the actual Bangalore coordinates. The driver location is simulated and updates with each refresh.")
        
        except Exception as e:
            st.error(f"❌ Error in map display: {e}")
            st.info("Please check if folium and streamlit-folium are properly installed")
    
    def display_traffic_analysis_map(self):
        """Display traffic analysis map for traffic jam scenarios"""
        try:
            st.subheader("🚦 Traffic Analysis - Bangalore Highway")
            
            # Create traffic analysis map
            map_obj = self.create_traffic_analysis_map()
            
            # Display map
            try:
                folium_static(map_obj, width=700, height=500)
                st.success("🗺️ Traffic analysis map loaded successfully!")
            except Exception as map_error:
                st.error(f"❌ Error displaying map: {map_error}")
                st.info("Trying alternative map display...")
                try:
                    st.components.v1.html(map_obj._repr_html_(), height=500)
                    st.success("✅ Map displayed using HTML fallback!")
                except Exception as html_error:
                    st.error(f"❌ HTML fallback also failed: {html_error}")
            
            # Display traffic information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Accident Location", "Highway 1")
            
            with col2:
                st.metric("Traffic Level", "🔴 High")
            
            with col3:
                st.metric("Alternative Routes", "2 Available")
            
            # Traffic analysis details
            st.markdown("---")
            st.subheader("🚦 **Traffic Analysis Details**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔴 Accident Route (High Traffic):**")
                st.write("• Highway 1 - Major accident")
                st.write("• 5+ delivery vehicles affected")
                st.write("• Estimated delay: 45+ minutes")
                st.write("• Police and ambulance on scene")
            
            with col2:
                st.write("**🟢 Alternative Route (Low Traffic):**")
                st.write("• Via Marathahalli - Bellandur")
                st.write("• 2 delivery vehicles affected")
                st.write("• Estimated delay: 15 minutes")
                st.write("• Recommended for all deliveries")
            
            # Route coordinates
            st.markdown("---")
            st.subheader("📍 **Route Coordinates & Traffic Status**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔴 Accident Route Coordinates:**")
                accident_route = [
                    [12.9716, 77.5946],  # MG Road
                    [12.9789, 77.6417],  # Indiranagar (accident location)
                    [12.9349, 77.6055],  # Koramangala
                    [12.9141, 77.6417],  # HSR Layout
                    [12.9067, 77.5851]   # JP Nagar
                ]
                for i, coord in enumerate(accident_route):
                    if i == 1:  # Accident location
                        st.write(f"  **{i+1}.** [{coord[0]:.4f}, {coord[1]:.4f}] 🚨 ACCIDENT")
                    else:
                        st.write(f"  **{i+1}.** [{coord[0]:.4f}, {coord[1]:.4f}]")
            
            with col2:
                st.write("**🟢 Alternative Route Coordinates:**")
                alt_route = [
                    [12.9716, 77.5946],  # MG Road
                    [12.9498, 77.6964],  # Marathahalli (avoiding accident)
                    [12.9349, 77.6749],  # Bellandur
                    [12.9141, 77.6417],  # HSR Layout
                    [12.9067, 77.5851]   # JP Nagar
                ]
                for i, coord in enumerate(alt_route):
                    if i == 1:  # Alternative path
                        st.write(f"  **{i+1}.** [{coord[0]:.4f}, {coord[1]:.4f}] 🟢 ALTERNATIVE")
                    else:
                        st.write(f"  **{i+1}.** [{coord[0]:.4f}, {coord[1]:.4f}]")
            
            st.info("🚦 **Traffic Info:** Red route shows accident location with high traffic. Green route is the recommended alternative with minimal delays.")
            
        except Exception as e:
            st.error(f"❌ Error in traffic analysis map display: {e}")
            st.info("Please check if folium and streamlit-folium are properly installed")
    
    def display_reroute_options(self):
        """Display rerouting options"""
        st.subheader("🔄 Route Optimization Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚗 Show Current Route", key="current_route"):
                self.display_live_driver_map("current_route")
        
        with col2:
            if st.button("🟢 Optimize Route", key="optimal_route"):
                self.display_live_driver_map("optimal_route")
                st.success("✅ Route optimized! ETA reduced by 15 minutes.")
        
        with col3:
            if st.button("🟠 Emergency Route", key="emergency_route"):
                self.display_live_driver_map("emergency_route")
                st.warning("⚠️ Emergency route activated. Longer but safer path.")
    
    def handle_map_action(self, action: str):
        """Handle map-related actions from interactive buttons"""
        if action == "show_live_map":
            self.display_live_driver_map("current_route")
            return "Live driver map displayed"
        
        elif action == "reroute_best_path":
            self.display_live_driver_map("optimal_route")
            return "Route optimized successfully"
        
        else:
            return "Unknown map action"

# Global map visualizer instance
map_visualizer = BangaloreMapVisualizer()
