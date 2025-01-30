// Modified from librealsense examples
// Copyright(c) 2019 Intel Corporation. All Rights Reserved.

#include <librealsense2/rs.hpp>
#include <iostream>
#include <iomanip>
#include <thread>
#include <mutex>
#include <stdio.h>
#include <memory>
#include <functional>
#include <thread>
#include <string.h>
#include <chrono>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <csignal>

volatile std::sig_atomic_t signalStatus = 0;
void sigintHandler(int signal)
{
    signalStatus = signal;
    std::cout << "\nInterrupt signal (" << signal << ") received.\n";
}

std::string filename = "test.bag";
int duration = 6000;

void print_usage()
{
    printf("\nUsage: iqr-multivideo -f <test.bag> -t <# seconds>\n\n");
}

void parseArgs(int argc, char **argv)
{
    int c;
    while ((c = getopt(argc, argv, "hf:t:")) != -1)
    {
        switch (c)
        {
        case 'h':
            print_usage();
            exit(0);
        case 'f':
            filename = optarg;
            break;
        case 't':
            duration = atoi(optarg);
            break;
        }
    }

    std::cout << "Capturing " << duration << " seconds to " << filename << std::endl;
}

int main(int argc, char *argv[])
try
{
    // Parse Arguments
    parseArgs(argc, argv);

    // Signal Handler for SIGINT
    struct sigaction new_action;
    new_action.sa_handler = sigintHandler;
    sigemptyset(&new_action.sa_mask);
    new_action.sa_flags = 0;
    sigaction(SIGINT, &new_action, NULL);

    rs2::pipeline pipe;
    rs2::config cfg;
    cfg.enable_record_to_file(filename);
    cfg.disable_all_streams();
    cfg.enable_stream(RS2_STREAM_COLOR, 640, 480, RS2_FORMAT_RGB8, 30);

    std::mutex m;
    auto callback = [&](const rs2::frame &frame)
    {
        std::lock_guard<std::mutex> lock(m);
        auto t = std::chrono::system_clock::now();

        static auto tk = t;
        static auto t0 = t;
        if (t - tk >= std::chrono::seconds(1))
        {
            std::cout << "\r" << std::setprecision(3) << std::fixed
                      << "Recording t = " << std::chrono::duration_cast<std::chrono::seconds>(t - t0).count() << "s" << std::flush;
            tk = t;
        }
    };

    rs2::pipeline_profile profiles = pipe.start(cfg, callback);

    auto t = std::chrono::system_clock::now();
    auto t0 = t;
    while (!signalStatus && t - t0 <= std::chrono::milliseconds((unsigned)(duration * 1000)))
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        t = std::chrono::system_clock::now();
    }
    std::cout << "\nFinished" << std::endl;

    pipe.stop();

    return EXIT_SUCCESS;
}
catch (const rs2::error &e)
{
    std::cerr << "RealSense error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}
catch (const std::exception &e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}