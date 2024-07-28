`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/21/2024 10:48:36 AM
// Design Name: 
// Module Name: basys_wrapper
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module basys_wrapper(
    input clk,
    // swith and led 
    input [15:0] sw, 
    output [15:0] led,
    
    // Seven Segment Display Outputs
    output [6:0] seg,
    output [3:0] an, 
    output dp
    );
    
    // tree module input/outputs 
    wire rst_n;
    
    reg [7:0] ui_in;
    reg [7:0] uo_out;
    
    // not used inputs 
    reg ena = 1;
    reg [7:0] uio_oe = 0;   
    reg [7:0] uio_out = 0;  
    reg [7:0] uio_in = 0;
    
    // debug outputs 
    reg [4:0] input_ready;
    reg [24:0] img;
    
  
    assign rst_n = sw[15];
    // instatiating tree module 
    tt_um_COLVERTYETY_top dut(.*);
    
    // instatiating 7 seg display module 
    sev_seg display(
        .in(uo_out),
        .clk(clk),
        .a_to_g(seg),
        .an(an),
        .dp(dp)
    );
    
    
    // assigning inputs 
    always_ff @(posedge clk) begin 
        ui_in <= {sw[3], sw[4], sw[5], sw[6], sw[7], sw[2:0]};
    end 
    
    // debugging inputs 
    
     assign led[0] = input_ready[0];
     assign led[1] = input_ready[1];
     assign led[2] = input_ready[2];
     assign led[3] = input_ready[3];
     assign led[4] = input_ready[4];
     
     reg [31:0] counter = 0;
     reg [2:0] counter2 = 0;
     
     reg [4:0] led_reg;
     reg [2:0] led_reg_num;
     
     always_ff @ (posedge clk) begin 
        counter = counter + 1;
        
        if (counter == 150000000) begin 
            counter <= 0;
            counter2 <= counter2 + 1;
        end 
        
        if (counter2 == 5) begin 
            counter2 <= 0;
        end 
        
        
        case(counter2)
            
            0: begin 
                led_reg <= img[4:0];
                led_reg_num <= 1;
            end 
            1: begin 
                led_reg <= img[9:5];
                led_reg_num <= 2;
            end 
            2: begin 
                led_reg <= img[14:10];
                led_reg_num <= 3;
            end 
            3: begin 
                led_reg <= img[19:15];
                led_reg_num <= 4;
            end 
            4: begin 
                led_reg <= img[24:20];
                led_reg_num <= 5;
            end 
        
        endcase
     
     end 
     
     assign led[10:6] = led_reg;
     assign led[14:12] = led_reg_num;
        

    //assigning outputs 
    
    
    
endmodule
