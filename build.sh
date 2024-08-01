docker build --build-arg http_proxy=http://$http_proxy \
             --build-arg https_proxy=http://$http_proxy \
              -t data-viz-cvlab:0.1  \
              .