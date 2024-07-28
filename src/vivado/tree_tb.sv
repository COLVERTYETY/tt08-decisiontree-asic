`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 07/20/2024 03:08:07 PM
// Design Name: 
// Module Name: tree_tb
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


module tree_tb();
    
    // input signals 
    reg clk;
    localparam T = 1000;
    always begin 
        clk = 1;
        #(T/2);
        clk = 0;
        #(T/2);
    end 
    
    reg rst_n;
    
    reg [7:0] ui_in;
    reg [7:0] uo_out;
    
    // not used inputs 
    reg ena = 1;
    wire [7:0] uio_oe;   
    wire [7:0] uio_out;  
    reg [7:0] uio_in;
    
    tt_um_COLVERTYETY_top dut(.*);
    
//    initial begin 
//        rst_n = 0;
        
//        repeat(20) begin 
//             @(posedge clk);
//        end 
        
//        rst_n = 1;
//        ui_in = 8'b
    
//    end 
    integer fd, fd2, status, status2;
    string input_file = "C:/Users/guoyi/Desktop/tinytapeout/tt08-decisiontree-asic/tests/test1.txt";
    string input_file_y = "C:/Users/guoyi/Desktop/tinytapeout/tt08-decisiontree-asic/tests/test1_y.txt";
    
    integer input_count = 0;
    
    reg [4:0] str;
    reg [7:0] y;
    reg [2:0] pos_count = 5;
    
    initial begin  
        fd = $fopen(input_file, "r");  
        fd2 = $fopen(input_file_y, "r");
        
        // Keep reading lines until EOF is found  
        while (! $feof(fd)) begin  
            @(posedge clk);
            // Get current line into the variable 'str'  
            status = $fscanf(fd, "%b", str); 
            
            
            // Display contents of the variable  
            $display("%b", str);  
            
            if (str == 5'b11111 && pos_count == 5) begin 
                
                pos_count = 0;
                status2 = $fscanf(fd2, "%d", y);
                input_count = input_count + 1;
                repeat(5) @(posedge clk);
                
                rst_n = 0;
                @(posedge clk);
                continue;
            end 
            
            else begin 
                rst_n = 1;
                ui_in = {str[0], str[1], str[2], str[3], str[4], pos_count};
                pos_count = pos_count + 1;
            
            end 
        end  
        $fclose(fd);  
        
        $finish;
    end  
    

    
endmodule
